"""Check-in without creative intent, and Soundspace with real songs."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

import storage
import views

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


def test_every_soundspace_vibe_has_real_songs_and_no_audio():
    for name in views.VIBE_SONGS:
        songs = views.vibe_songs(name)
        assert len(songs) == 4 and all(s["title"] and s["artist"] for s in songs)
    storage.delete_everything()
    at = app_on("Soundspace")
    assert not at.exception and not at.get("audio")
    assert any("track-links" in h.proto.body for h in at.get("html"))
