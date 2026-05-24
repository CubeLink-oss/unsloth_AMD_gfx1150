# SPDX-License-Identifier: AGPL-3.0-only
# Copyright 2026-present the Unsloth AI Inc. team. All rights reserved. See /studio/LICENSE.AGPL-3.0

import os

from utils.paths.storage_roots import setup_huggingface_download_env


def test_huggingface_download_env_defaults_to_fast_xet(monkeypatch):
    keys = (
        "HF_XET_HIGH_PERFORMANCE",
        "HF_XET_NUM_CONCURRENT_RANGE_GETS",
        "HF_HUB_DOWNLOAD_TIMEOUT",
        "HF_HUB_ETAG_TIMEOUT",
    )
    for key in keys:
        monkeypatch.delenv(key, raising = False)

    setup_huggingface_download_env()

    assert os.environ["HF_XET_HIGH_PERFORMANCE"] == "1"
    assert os.environ["HF_XET_NUM_CONCURRENT_RANGE_GETS"] == "64"
    assert os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] == "60"
    assert os.environ["HF_HUB_ETAG_TIMEOUT"] == "30"


def test_huggingface_download_env_preserves_user_values(monkeypatch):
    monkeypatch.setenv("HF_XET_HIGH_PERFORMANCE", "0")
    monkeypatch.setenv("HF_XET_NUM_CONCURRENT_RANGE_GETS", "16")
    monkeypatch.setenv("HF_HUB_DOWNLOAD_TIMEOUT", "120")
    monkeypatch.setenv("HF_HUB_ETAG_TIMEOUT", "5")

    setup_huggingface_download_env()

    assert os.environ["HF_XET_HIGH_PERFORMANCE"] == "0"
    assert os.environ["HF_XET_NUM_CONCURRENT_RANGE_GETS"] == "16"
    assert os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] == "120"
    assert os.environ["HF_HUB_ETAG_TIMEOUT"] == "5"
