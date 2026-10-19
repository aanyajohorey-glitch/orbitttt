"""
voice.py
Voice check-ins: speak instead of typing.

The browser records audio with st.audio_input. To turn speech into text,
ORBIT uses faster-whisper (a free, offline speech-recognition model) IF it
is installed. If not, the voice feature politely explains how to enable it,
and everything else keeps working.
"""
import io

import streamlit as st

WHISPER_SIZE = "base"  # "tiny" is faster, "small" is more accurate


def available():
    try:
        import faster_whisper  # noqa: F401
        return True
    except ImportError:
        return False


@st.cache_resource(show_spinner="Loading the speech model…")
def _model():
    from faster_whisper import WhisperModel
    return WhisperModel(WHISPER_SIZE, device="cpu", compute_type="int8")


def transcribe(audio_bytes):
    """Return the words spoken in a recording (English or Hindi)."""
    segments, _ = _model().transcribe(io.BytesIO(audio_bytes), vad_filter=True)
    return " ".join(segment.text.strip() for segment in segments).strip()
