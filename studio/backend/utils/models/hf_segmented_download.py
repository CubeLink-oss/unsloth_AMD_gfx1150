# SPDX-License-Identifier: AGPL-3.0-only
# Copyright 2026-present the Unsloth AI Inc. team. All rights reserved. See /studio/LICENSE.AGPL-3.0

from __future__ import annotations

import os
import shutil
import sys
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path
from typing import Callable, Optional

import requests
from huggingface_hub import hf_hub_url
from huggingface_hub.file_download import get_hf_file_metadata

from utils.paths.storage_roots import cache_root


ProgressCallback = Callable[[int, int], None]


def _format_bytes(value: float) -> str:
    units = ("B", "KB", "MB", "GB", "TB")
    size = float(max(value, 0.0))
    for unit in units:
        if size < 1024.0 or unit == units[-1]:
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024.0


def _format_duration(seconds: float) -> str:
    if seconds <= 0 or seconds == float("inf"):
        return "--"
    total = int(seconds)
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}h {minutes:02d}m"
    if minutes:
        return f"{minutes}m {secs:02d}s"
    return f"{secs}s"


def _bar(percent: float, width: int) -> str:
    pct = max(0.0, min(1.0, percent))
    filled = int(round(pct * width))
    return "[" + ("#" * filled) + ("-" * (width - filled)) + "]"


class _LiveSegmentRenderer:
    def __init__(
        self,
        *,
        filename: str,
        total_size: int,
        total_parts: int,
        states: dict[int, dict[str, int | str]],
        lock: threading.Lock,
        workers: int,
    ) -> None:
        self.filename = filename
        self.total_size = total_size
        self.total_parts = total_parts
        self.states = states
        self.lock = lock
        self.rows = max(4, min(workers, int(os.environ.get("UNSLOTH_HF_PROGRESS_ROWS", "16"))))
        self.enabled = (
            _truthy(os.environ.get("UNSLOTH_HF_LIVE_PROGRESS"), default = True)
            and sys.stderr.isatty()
            and os.environ.get("NO_COLOR") is None
        )
        self.started = time.monotonic()
        self.last_bytes = 0
        self.last_time = self.started
        self.speed = 0.0
        self.lines_rendered = 0

    def _snapshot(self) -> tuple[int, list[dict[str, int | str]]]:
        with self.lock:
            parts = [dict(state) for _, state in sorted(self.states.items())]
        downloaded = sum(
            min(int(part["downloaded"]), int(part["total"])) for part in parts
        )
        return downloaded, parts

    def render(self, *, force: bool = False, merging: bool = False) -> None:
        if not self.enabled:
            return
        now = time.monotonic()
        if not force and now - self.last_time < 0.5:
            return
        downloaded, parts = self._snapshot()
        elapsed = max(now - self.started, 0.001)
        instant_elapsed = max(now - self.last_time, 0.001)
        instant_speed = (downloaded - self.last_bytes) / instant_elapsed
        if instant_speed > 0:
            self.speed = instant_speed if self.speed <= 0 else (self.speed * 0.7 + instant_speed * 0.3)
        avg_speed = downloaded / elapsed
        speed = self.speed or avg_speed
        remaining = max(self.total_size - downloaded, 0)
        eta = remaining / speed if speed > 0 else float("inf")

        done_count = sum(1 for part in parts if part["status"] == "done")
        active = [part for part in parts if part["status"] == "active"]
        retrying = sum(1 for part in parts if part["status"] == "retrying")
        queued = self.total_parts - done_count - len(active) - retrying
        percent = downloaded / self.total_size if self.total_size else 0.0
        title = f"Downloading {self.filename}"
        if merging:
            title = f"Merging {self.filename}"
        lines = [
            title[:120],
            (
                f"Overall {_bar(percent, 34)} {percent * 100:5.1f}%  "
                f"{_format_bytes(downloaded)}/{_format_bytes(self.total_size)}  "
                f"{_format_bytes(speed)}/s  ETA {_format_duration(eta)}"
            ),
            (
                f"Segments {done_count}/{self.total_parts} done, "
                f"{len(active)} active, {max(queued, 0)} queued, {retrying} retrying"
            ),
            "Active segments:",
        ]
        for part in active[: self.rows]:
            part_total = int(part["total"])
            part_done = min(int(part["downloaded"]), part_total)
            part_pct = part_done / part_total if part_total else 0.0
            lines.append(
                f"  {int(part['index']) + 1:03d}/{self.total_parts:03d} "
                f"{_bar(part_pct, 26)} {part_pct * 100:5.1f}%  "
                f"{_format_bytes(part_done)}/{_format_bytes(part_total)}"
            )
        while len(lines) < 4 + self.rows:
            lines.append("")

        if self.lines_rendered:
            sys.stderr.write(f"\x1b[{self.lines_rendered}F")
        for line in lines:
            sys.stderr.write("\x1b[2K" + line + "\n")
        sys.stderr.flush()
        self.lines_rendered = len(lines)
        self.last_time = now
        self.last_bytes = downloaded

    def finish(self, *, message: str) -> None:
        if not self.enabled:
            return
        self.render(force = True)
        sys.stderr.write(message + "\n")
        sys.stderr.flush()
        self.lines_rendered = 0


def _truthy(value: str | None, *, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _safe_repo_dir(repo_id: str) -> str:
    return f"models--{repo_id.replace('/', '--')}"


def _part_path(parts_dir: Path, index: int) -> Path:
    return parts_dir / f"{index:05d}.part"


def _download_range(
    *,
    url: str,
    destination: Path,
    index: int,
    start: int,
    end: int,
    timeout: int,
    update_state: Callable[[int, int, str], None],
) -> int:
    existing = destination.stat().st_size if destination.exists() else 0
    expected = end - start + 1
    if existing >= expected:
        update_state(index, expected, "done")
        return expected

    update_state(index, existing, "active")
    headers = {"Range": f"bytes={start + existing}-{end}"}
    with requests.get(url, headers = headers, stream = True, timeout = timeout) as resp:
        if resp.status_code != 206:
            raise RuntimeError(f"range request returned HTTP {resp.status_code}")
        destination.parent.mkdir(parents = True, exist_ok = True)
        with destination.open("ab") as f:
            for chunk in resp.iter_content(chunk_size = 1024 * 1024):
                if chunk:
                    f.write(chunk)
                    existing += len(chunk)
                    update_state(index, min(existing, expected), "active")
    final = destination.stat().st_size
    if final != expected:
        raise RuntimeError(
            f"incomplete part {destination.name}: {final} bytes, expected {expected}"
        )
    update_state(index, expected, "done")
    return final


def segmented_hf_hub_download(
    *,
    repo_id: str,
    filename: str,
    token: Optional[str] = None,
    min_size_bytes: int = 1024**3,
    progress: Optional[ProgressCallback] = None,
) -> Optional[str]:
    """Download a large HF file via resumable parallel Range requests.

    Returns a local path when the segmented downloader handled the file.
    Returns None when callers should fall back to huggingface_hub.
    """
    if not _truthy(os.environ.get("UNSLOTH_HF_SEGMENTED_DOWNLOAD"), default = True):
        return None

    url = hf_hub_url(repo_id = repo_id, filename = filename)
    metadata = get_hf_file_metadata(
        url,
        token = token,
        timeout = int(os.environ.get("HF_HUB_ETAG_TIMEOUT", "30")),
    )
    if not metadata.location or not metadata.size or metadata.size < min_size_bytes:
        return None

    workers = max(1, int(os.environ.get("UNSLOTH_HF_DOWNLOAD_WORKERS", "16")))
    workers = min(workers, 32)
    timeout = max(30, int(os.environ.get("HF_HUB_DOWNLOAD_TIMEOUT", "60")))
    total_size = int(metadata.size)
    chunk_size = max(
        16 * 1024 * 1024,
        int(os.environ.get("UNSLOTH_HF_DOWNLOAD_CHUNK_MB", "64")) * 1024 * 1024,
    )

    revision = metadata.commit_hash or "main"
    target = (
        cache_root()
        / "hf-segmented"
        / _safe_repo_dir(repo_id)
        / revision
        / filename
    )
    if target.is_file() and target.stat().st_size == total_size:
        return str(target)

    parts_dir = target.with_suffix(target.suffix + ".parts")
    ranges: list[tuple[int, int, int]] = []
    start = 0
    index = 0
    while start < total_size:
        end = min(start + chunk_size - 1, total_size - 1)
        ranges.append((index, start, end))
        start = end + 1
        index += 1
    state_lock = threading.Lock()
    states: dict[int, dict[str, int | str]] = {}
    for part_index, part_start, part_end in ranges:
        expected = part_end - part_start + 1
        part = _part_path(parts_dir, part_index)
        existing = min(part.stat().st_size, expected) if part.exists() else 0
        status = "done" if existing >= expected else "queued"
        states[part_index] = {
            "index": part_index,
            "downloaded": existing,
            "total": expected,
            "status": status,
        }

    renderer = _LiveSegmentRenderer(
        filename = filename,
        total_size = total_size,
        total_parts = len(ranges),
        states = states,
        lock = state_lock,
        workers = workers,
    )

    def update_state(part_index: int, downloaded: int, status: str) -> None:
        with state_lock:
            state = states[part_index]
            state["downloaded"] = downloaded
            state["status"] = status

    def downloaded_bytes() -> int:
        with state_lock:
            return sum(
                min(int(state["downloaded"]), int(state["total"]))
                for state in states.values()
            )

    if progress is not None:
        progress(downloaded_bytes(), total_size)
    renderer.render(force = True)

    pending = {
        item
        for item in ranges
        if states[item[0]]["status"] != "done"
    }
    last_progress = 0.0
    with ThreadPoolExecutor(max_workers = workers) as pool:
        futures = {}
        while pending or futures:
            while pending and len(futures) < workers:
                item = pending.pop()
                part_index, part_start, part_end = item
                future = pool.submit(
                    _download_range,
                    url = metadata.location,
                    destination = _part_path(parts_dir, part_index),
                    index = part_index,
                    start = part_start,
                    end = part_end,
                    timeout = timeout,
                    update_state = update_state,
                )
                futures[future] = item

            done, _ = wait(futures, timeout = 1.0, return_when = FIRST_COMPLETED)
            now = time.monotonic()
            renderer.render()
            if progress is not None and now - last_progress >= 2.0:
                progress(downloaded_bytes(), total_size)
                last_progress = now

            for future in done:
                item = futures.pop(future)
                try:
                    future.result()
                except Exception:
                    update_state(item[0], int(states[item[0]]["downloaded"]), "retrying")
                    pending.add(item)
                    raise

    target.parent.mkdir(parents = True, exist_ok = True)
    tmp_target = target.with_suffix(target.suffix + ".tmp")
    renderer.render(force = True, merging = True)
    with tmp_target.open("wb") as out:
        for part_index, _, _ in ranges:
            with _part_path(parts_dir, part_index).open("rb") as part_file:
                shutil.copyfileobj(part_file, out, length = 1024 * 1024)
    if tmp_target.stat().st_size != total_size:
        tmp_target.unlink(missing_ok = True)
        raise RuntimeError("merged GGUF size did not match expected size")
    tmp_target.replace(target)
    shutil.rmtree(parts_dir, ignore_errors = True)
    if progress is not None:
        progress(total_size, total_size)
    elapsed = max(time.monotonic() - renderer.started, 0.001)
    renderer.finish(
        message = (
            f"Downloaded {filename}: {_format_bytes(total_size)} in "
            f"{_format_duration(elapsed)} "
            f"({_format_bytes(total_size / elapsed)}/s average)"
        )
    )
    return str(target)
