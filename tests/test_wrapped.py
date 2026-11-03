"""
Tests for the landing page, Settings menu, no background music, and My Galaxy -> Wrapped.
"""
from datetime import datetime, timedelta
from pathlib import Path

from streamlit.testing.v1 import AppTest

import storage
import wrapped
from journal import entries_table
from world_data import load_worlds

APP = str(Path(__file__).resolve().parents[1] / "app.py")
DAYS = [
    [("joy", 0.6), ("gratitude", 0.3), ("neutral", 0.1)],
    [("nervousness", 0.5), ("fear", 0.3), ("neutral", 0.2)],
    [("sadness", 0.6), ("neutral", 0.4)],
    [("joy", 0.7), ("excitement", 0.3)],
]


def add_days(count):
    world = load_worlds()[0]["name"]
    for i in range(count):
        emotions = DAYS[i % len(DAYS)]
        when = (datetime.now() - timedelta(days=i)).isoformat(timespec="seconds")
        storage.add_entry("Today", f"day {i}", emotions, world, created_at=when, primary=emotions[0][0])


def app_on(page):
    at = AppTest.from_file(APP, default_timeout=120)
    at.session_state.started = True
    at.session_state.page = page
    at.run()
    return at


def test_summary_counts_feelings_and_days():
    storage.delete_everything()
    add_days(4)
    facts = wrapped.summary(entries_table())
    assert facts["checkins"] == 4 and facts["days"] == 4
    assert facts["top_feelings"][0] == "joy"
    assert abs(sum(share for _, share in facts["emotions"]) - 1) < 1e-6
    assert facts["families"][0][0] == "Joy"
    assert facts["world"] == load_worlds()[0]["name"]


def test_painting_is_the_same_for_the_same_check_ins():
    families = [("Joy", 0.5), ("Sadness", 0.3), ("Fear", 0.2)]
    one, two = wrapped.painting(families, seed=3), wrapped.painting(families, seed=3)
    assert one.size == (900, 600) and one.tobytes() == two.tobytes()
    assert wrapped.painting(families, seed=4).tobytes() != one.tobytes()
    assert wrapped.painting([]).size == (900, 600)


def test_card_is_a_png():
    storage.delete_everything()
    add_days(3)
    facts = wrapped.summary(entries_table())
    data = wrapped.card_png(facts, wrapped.painting(facts["families"]), "30 days", "Asha")
    assert data[:8] == b"\x89PNG\r\n\x1a\n"


def test_wrapped_page_needs_a_few_check_ins():
    storage.delete_everything()
    add_days(1)
    at = app_on("Wrapped")
    assert not at.exception
    assert at.button(key="wrapped_checkin")


def test_wrapped_page_shows_painting_playlist_and_download():
    storage.delete_everything()
    add_days(5)
    at = app_on("Wrapped")
    assert not at.exception
    assert any(b.key == "wrapped_download" for b in at.get("download_button"))
    assert at.get("image")


def test_no_about_tab_and_no_panic_button():
    storage.delete_everything()
    at = app_on("Home")
    keys = {b.key for b in at.button}
    assert "tab_About" not in keys and not any("panic" in (k or "") for k in keys)


def test_no_background_music_anywhere():
    storage.delete_everything()
    for page in ("Create", "Home", "Wrapped"):
        at = app_on(page)
        assert not at.exception and not at.get("audio")
    assert not any(t.key == "set_bg_music" for t in at.toggle)


REMOVED_PAGES = ["Companion", "Calm Room", "Reach Out", "Letters", "Safety plan", "Mood Lab", "Journal"]


def test_removed_pages_are_gone_from_every_tab():
    storage.delete_everything()
    for page in ("Home", "Wrapped", "Create"):
        at = app_on(page)
        keys = {b.key for b in at.button}
        assert not any(f"nav_{p}" in keys for p in REMOVED_PAGES)
    import games
    assert set(games.GAMES) == {"planet_builder", "tiny_wins", "crack_glass", "mandala"}


def test_a_check_in_runs_without_links_to_removed_pages():
    storage.delete_everything()
    storage.set_setting("demo_mode", "1")
    at = app_on("Home")
    at.text_area(key="home_text").input("I am so stressed about my exams tomorrow").run()
    at.button(key="find_orbit").click().run()
    assert not at.exception and at.session_state.home_result
    keys = {b.key for b in at.button}
    assert not keys & {"home_talk", "home_to_lab", "home_tool", "today_galaxy"}
    at.button(key="today_finish").click().run()
    assert not at.exception and at.button(key="save_home_result")
