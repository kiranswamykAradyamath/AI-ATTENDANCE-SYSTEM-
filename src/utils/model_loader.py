"""
src/utils/model_loader.py

Startup helper that ensures all ML model weights are present before any
pipeline code runs. Works identically on local dev and Streamlit Cloud.
"""

from __future__ import annotations

import os
import urllib.request
from collections.abc import Callable
from pathlib import Path

import streamlit as st

_VGG_FILENAME = "vgg_face_weights.h5"
_VGG_URL = (
    "https://github.com/serengil/deepface_models/releases/download/v1.0/"
    "vgg_face_weights.h5"
)


def _vgg_weights_path() -> Path:
    """
    Return the path where DeepFace will look for the VGG-Face weights.
    This respects the DEEPFACE_HOME env-var that app.py sets before import.
    """
    deepface_home = os.environ.get("DEEPFACE_HOME") or str(Path.home())
    return Path(deepface_home) / ".deepface" / "weights" / _VGG_FILENAME


def _vgg_weights_present() -> bool:
    path = _vgg_weights_path()
    return path.exists() and path.stat().st_size > 100_000_000


def _download_vgg_weights(
    reporthook: Callable[[int, int, int], None] | None = None,
) -> None:
    """Download VGG-Face weights with an optional urllib progress hook."""
    target = _vgg_weights_path()
    target.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = target.with_suffix(".h5.tmp")

    try:
        urllib.request.urlretrieve(_VGG_URL, tmp_path, reporthook=reporthook)
        tmp_path.rename(target)
    except Exception as exc:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise RuntimeError(
            f"Failed to download VGG-Face weights from {_VGG_URL}. "
            f"Please download manually and place at:\n{target}"
        ) from exc


def _prewarm_voice_encoder() -> None:
    """
    Pre-warm the Resemblyzer VoiceEncoder so its model downloads, if needed,
    happen at startup rather than mid-session. Failures are non-fatal.
    """
    try:
        from resemblyzer import VoiceEncoder

        VoiceEncoder()
    except Exception:
        pass


@st.cache_resource(show_spinner=False)
def _ensure_models_ready_cached() -> bool:
    """
    Cached model setup. Keep Streamlit UI calls out of this function so cached
    message replay cannot fail on reruns.
    """
    if not _vgg_weights_present():
        _download_vgg_weights()

    _prewarm_voice_encoder()
    return True


def ensure_models_ready() -> bool:
    """
    Called at app startup. Returns True when everything is ready, False if a
    non-fatal setup issue occurred.
    """
    if _vgg_weights_present():
        return _ensure_models_ready_cached()

    progress_bar = st.progress(0, text="Downloading VGG-Face model weights...")

    def _report(block_num: int, block_size: int, total_size: int) -> None:
        if total_size <= 0:
            return

        downloaded = min(block_num * block_size, total_size)
        pct = downloaded / total_size
        mb_done = downloaded / 1_048_576
        mb_total = total_size / 1_048_576
        progress_bar.progress(
            pct,
            text=f"Downloading VGG-Face weights... {mb_done:.0f} / {mb_total:.0f} MB",
        )

    with st.spinner("First-time setup: downloading face recognition model (~580 MB)..."):
        try:
            _download_vgg_weights(reporthook=_report)
        except RuntimeError as exc:
            progress_bar.empty()
            st.error(str(exc))
            return False

    progress_bar.empty()
    st.toast("Face model downloaded successfully!")
    return _ensure_models_ready_cached()
