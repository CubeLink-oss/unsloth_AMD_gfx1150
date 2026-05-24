# SPDX-License-Identifier: AGPL-3.0-only
# Copyright 2026-present the Unsloth AI Inc. team. All rights reserved. See /studio/LICENSE.AGPL-3.0

from __future__ import annotations

import os
import shutil
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path
from typing import Callable, Optional

import requests
from huggingface_hub import hf_hub_url
from huggingface_hub.file_download import get_hf_file_metadata

from utils.paths.storage_roots import cache_root


ProgressCallback = Callable[[int, int], None]


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
    start: int,
    end: int,
    timeout: int,
) -> int:
    existing = destination.stat().st_size if destination.exists() else 0
    expected = end - start + 1
    if existing >= expected:
        return expected

    headers = {"Range": f"bytes={start + existing}-{end}"}
    with requests.get(url, headers = headers, stream = True, timeout = timeout) as resp:
        if resp.status_code != 206:
            raise RuntimeError(f"range request returned HTTP {resp.status_code}")
        destination.parent.mkdir(parents = True, exist_ok = True)
        with destination.open("ab") as f:
            for chunk in resp.iter_content(chunk_size = 1024 * 1024):
                if chunk:
                    f.write(chunk)
    final = destination.stat().st_size
    if final != expected:
        raise RuntimeError(
            f"incomplete part {destination.name}: {final} bytes, expected {expected}"
        )
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

    def downloaded_bytes() -> int:
        done = 0
        for part_index, part_start, part_end in ranges:
            expected = part_end - part_start + 1
            part = _part_path(parts_dir, part_index)
            if part.exists():
                done += min(part.stat().st_size, expected)
        return done

    if progress is not None:
        progress(downloaded_bytes(), total_size)

    pending = set(ranges)
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
                    start = part_start,
                    end = part_end,
                    timeout = timeout,
                )
                futures[future] = item

            done, _ = wait(futures, timeout = 1.0, return_when = FIRST_COMPLETED)
            now = time.monotonic()
            if progress is not None and now - last_progress >= 2.0:
                progress(downloaded_bytes(), total_size)
                last_progress = now

            for future in done:
                item = futures.pop(future)
                try:
                    future.result()
                except Exception:
                    pending.add(item)
                    raise

    target.parent.mkdir(parents = True, exist_ok = True)
    tmp_target = target.with_suffix(target.suffix + ".tmp")
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
    return str(target)
