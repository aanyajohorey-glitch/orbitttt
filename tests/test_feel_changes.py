"""Check-in without creative intent, and no Soundspace page."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

import storage

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def app_on(page):
    at = AppTest.from_file(APP, default_timeout=120)
    at.session_state.started = True
    at.session_state.page = page
    at.run()
    return at


def test_check_in_has_no_creative_intent_choice():
    storage.delete_everything()
    at = app_on("Home")
    assert not at.exception
    assert not any(p.key == "home_intent" for p in at.get("button_group"))
    assert not any("Creative intent" in (getattr(p, "label", "") or "") for p in at.get("button_group"))


def test_soundspace_is_gone_from_feel():
    storage.delete_everything()
    at = app_on("Home")
    assert not at.exception
    assert not any(b.key == "nav_Soundspace" for b in at.button)
