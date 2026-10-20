"""
Shared test setup.

- Puts the project folder on the import path.
- Points ORBIT at a TEMPORARY database, so tests never touch real data.
- Provides a clean Streamlit session state for tests of the game rules.
"""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["ORBIT_DB"] = str(Path(tempfile.mkdtemp()) / "orbit_test.db")

import pytest  # noqa: E402
import streamlit as st  # noqa: E402

import storage  # noqa: E402

storage.init()


@pytest.fixture
def session():
    """A fresh, minimal ORBIT session (tokens, messages, collection)."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.tokens = 3
    st.session_state.flash = []
    st.session_state.collection = []
    storage.delete_everything()
    yield st.session_state


def model_available():
    try:
        import emotion_model
        emotion_model.load_model()
        return True
    except Exception:
        return False


needs_model = pytest.mark.skipif(not model_available(), reason="emotion model not downloaded")
