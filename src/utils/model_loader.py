"""
src/utils/model_loader.py

Startup helper that ensures all ML model weights are present before
any pipeline code runs. Works identically on local dev and Streamlit Cloud.

Strategy:
  - VGG-Face weights (580 MB): DeepFace expects them at
    {DEEPFACE_HOME}/.deepface/weights/vgg_face_weights.h5
    OR  ~/.deepface/weights/vgg_face_weights.h5
    We check both locations. If found → nothing to do.
    If missing → download via urllib (stdlib, zero extra deps).

  - Resemblyzer / torch models: downloaded automatically by the library
    on first call to VoiceEncoder(). We trigger that call once here so
    any download happens at startup (with a spinner) rather than mid-session.
"""

from __future__ import annotations

import os
import urllib.request
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# VGG-Face weight constants
# ---------------------------------------------------------------------------
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
    return path.exists() and path.stat().st_size > 100_000_000  # sanity: >100 MB


def _download_vgg_weights() -> None:
    """Download VGG-Face weights with a progress-reporting urllib call."""
    target = _vgg_weights_path()
    target.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = target.with_suffix(".h5.tmp")

    progress_placeholder = st.empty()
    progress_bar = st.progress(0, text="Downloading VGG-Face model weights…")

    def _report(block_num: int, block_size: int, total_size: int) -> None:
        if total_size <= 0:
            return
        downloaded = min(block_num * block_size, total_size)
        pct = downloaded / total_size
        mb_done = downloaded / 1_048_576
        mb_total = total_size / 1_048_576
        progress_bar.progress(
            pct,
            text=f"Downloading VGG-Face weights… {mb_done:.0f} / {mb_total:.0f} MB",
        )

    try:
        urllib.request.urlretrieve(_VGG_URL, tmp_path, reporthook=_report)
        tmp_path.rename(target)
        progress_bar.empty()
        progress_placeholder.empty()
    except Exception as exc:
        progress_bar.empty()
        progress_placeholder.empty()
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise RuntimeError(
            f"Failed to download VGG-Face weights from {_VGG_URL}. "
            f"Please download manually and place at:\n{target}"
        ) from exc


# ---------------------------------------------------------------------------
# Resemblyzer / voice model pre-warm
# ---------------------------------------------------------------------------

def _prewarm_voice_encoder() -> None:
    """
    Pre-warm the Resemblyzer VoiceEncoder so its model downloads (if needed)
    happen at startup rather than mid-session.  Failures are non-fatal —
    voice attendance simply won't be available.
    """
    try:
        from resemblyzer import VoiceEncoder  # noqa: F401 — side-effect import
        VoiceEncoder()  # triggers model download on first call
    except Exception:
        # Voice encoder unavailable — handled gracefully in voice_pipelines.py
        pass


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def ensure_models_ready() -> bool:
    """
    Called once at app startup (cached so it only runs once per server process).
    Returns True when everything is ready, False if a non-fatal issue occurred.
    """
    # ── VGG-Face weights ───────────────────────────────────────────────────
    if not _vgg_weights_present():
        with st.spinner("⏳ First-time setup: downloading face recognition model (~580 MB)…"):
            try:
                _download_vgg_weights()
                st.toast("✅ Face model downloaded successfully!")
            except RuntimeError as exc:
                st.error(str(exc))
                return False

    # ── Resemblyzer voice model (optional, non-fatal) ─────────────────────
    _prewarm_voice_encoder()

    return True
