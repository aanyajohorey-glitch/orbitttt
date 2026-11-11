"""Tests for online_sources.py. No internet: every service is replaced by a small saved sample."""
import pytest

import creative
import creative_match as cm
import demo_mode
import online_sources as o
import vibe

SENT = []


def unsplash_item(i, title, colour, author):
    return {"id": f"u{i}", "urls": {"small": f"https://images.unsplash.com/{i}?ixid=x"},
            "links": {"html": f"https://unsplash.com/photos/{i}"}, "alt_description": title, "tags": [],
            "color": colour, "user": {"name": author, "links": {"html": f"https://unsplash.com/@{author}"}}}


def openverse_item(i, title, tags, author):
    return {"id": f"ov{i}", "thumbnail": f"https://api.openverse.org/thumb/{i}", "foreign_landing_url": "https://x.org",
            "title": title, "tags": [{"name": t} for t in tags], "creator": author, "creator_url": "",
            "license": "by", "license_version": "2.0", "license_url": "https://creativecommons.org/licenses/by/2.0/",
            "attribution": f'"{title}" by {author}, CC BY 2.0'}


FAKE = {
    "unsplash": {"results": [
        unsplash_item(1, "red roses by candlelight on a dark table", "#5C1A2B", "ana"),
        unsplash_item(2, "burgundy velvet curtain", "#722F37", "ben"),
        unsplash_item(3, "red roses candlelight romantic", "#6A2030", "ana"),
        unsplash_item(4, "halloween skull with roses and candles", "#2B2629", "cat"),
        unsplash_item(5, "blue car parked by roses", "#2244AA", "dev")]},
    "openverse": {"results": [
        openverse_item(1, "Candlelit dinner with roses", ["candlelit", "dinner", "romantic"], "eve"),
        openverse_item(2, "Burgundy velvet chair", ["burgundy", "velvet"], "fay"),
        openverse_item(3, "Office printer", ["office"], "gus")]},
    "pixabay": {"hits": [
        {"id": 9, "webformatURL": "https://pixabay.com/get/9.jpg", "pageURL": "https://pixabay.com/9",
         "tags": "damask, pattern, burgundy, ornament", "user": "hal", "user_id": 1}]},
    "lastfm": {"tracks": {"track": [
        {"name": "Velvet Night", "artist": {"name": "The Romantics"}, "url": "https://last.fm/1"},
        {"name": "Party Party", "artist": {"name": "Fun Band"}, "url": "https://last.fm/2"},
        {"name": "Clair de Lune", "artist": {"name": "Claude Debussy"}, "url": "https://last.fm/3"}]}},
    "musicbrainz": {"recordings": [{"id": "abc", "score": 100, "first-release-date": "1999-01-01",
                                    "tags": [{"name": "romantic"}, {"name": "chamber pop"}]}]},
    "googlefonts": {"items": [{"family": "Playfair Display", "category": "serif"},
                              {"family": "Libre Caslon Text", "category": "serif"},
                              {"family": "Great Vibes", "category": "handwriting"},
                              {"family": "Roboto", "category": "sans-serif"}]},
}


@pytest.fixture
def fake_internet(monkeypatch):
    SENT.clear()
    o._cache.clear()
    for queue in o._calls.values():
        queue.clear()

    def fake_get_json(source, url, params=None, headers=None, counted=True):
        SENT.append((source, dict(params or {})))
        if source == "musicbrainz" and "Party" in str(params):
            return {"recordings": []}
        return FAKE[source]
    monkeypatch.setattr(o, "get_json", fake_get_json)
    monkeypatch.setattr(o, "secret", lambda name: "test-key")
    return SENT


def brief_for(idea):
    result = demo_mode.interpret_offline(idea)
    vector = vibe.build(idea, result["emotions"])
    return vector, vector["match"], cm.brief(vector["match"])


def test_online_sources_are_off_while_testing():
    assert not o.enabled()


def test_image_score_follows_the_documented_rules():
    keywords = ["roses", "candlelight", "burgundy", "velvet"]
    image = {"title": "red roses by candlelight", "tags": ["velvet"], "colour": "#5C1A2B"}
    score, hits, avoided = o.score_image(image, keywords, ["skull"], ["#5C1A2B"])
    assert score == pytest.approx(0.6 * 1 + 0.3 * 1 + 0.1) and not avoided
    skull = {"title": "skull with roses", "tags": [], "colour": None}
    score, _, avoided = o.score_image(skull, keywords, ["skull"], ["#5C1A2B"])
    assert avoided == ["skull"] and score < o.KEEP_IMAGE


def test_moodboard_keeps_on_brief_images_with_credits_and_no_repeats(fake_internet):
    vector, found, brief = brief_for("Dark Romance")
    out = o.visuals(brief, found, creative.style_palette(vector, found))
    titles = [i["title"] for i in out["images"]]
    assert not any("skull" in t or "car" in t or "printer" in t.lower() for t in titles)
    authors = [i["author"] for i in out["images"]]
    assert len(authors) == len(set(authors))
    assert all(i["credit"] and i["licence"] and i["link"] for i in out["images"])
    assert {i["source"] for i in out["images"]} >= {"Unsplash", "Openverse"}


def test_typed_idea_is_cleaned_to_eight_words():
    text = ("Dark romance poster, mail me at asha@example.com or see https://x.com/a "
            "call 98765 43210 candles roses velvet rain night extra words")
    query = o.safe_query(text)
    assert "@" not in query and "http" not in query and "98765" not in query and "43210" not in query
    assert query.split() == ["Dark", "romance", "poster", "mail", "me", "at", "or", "see"]
    assert o.safe_query("") == ""


def test_typed_idea_is_the_first_search_but_not_sent_to_music_or_fonts(fake_internet):
    vector, found, brief = brief_for("a candlelit poster about Dark Romance")
    o.gather(brief, found, creative.style_palette(vector, found), [], ["Lora"],
             user_query="a candlelit poster about Dark Romance")
    image_searches = [(s, p) for s, p in fake_internet if s in ("unsplash", "openverse", "pixabay")]
    for source in ("unsplash", "openverse", "pixabay"):
        sent = [p.get("query") or p.get("q") for s, p in image_searches if s == source]
        assert "a candlelit poster about Dark Romance" in sent, source
    for source, params in fake_internet:
        if source in ("lastfm", "musicbrainz", "googlefonts"):
            assert "candlelit poster" not in str(params)


def test_without_typed_text_only_orbits_own_words_are_sent(fake_internet):
    vector, found, brief = brief_for("my secret diary entry about Dark Romance")
    out = o.gather(brief, found, creative.style_palette(vector, found), [], ["Lora"])
    assert out["images"]
    for _, params in fake_internet:
        assert "secret" not in str(params) and "diary" not in str(params)


def _build(monkeypatch, text, online=True, demo=False):
    """Run Create's real input handler and return the user_query it attached to the idea."""
    import streamlit as st
    import create_ui
    monkeypatch.setattr(o, "enabled", lambda: online)
    monkeypatch.setattr(demo_mode, "enabled", lambda: demo)
    monkeypatch.setattr(create_ui, "read_emotions", lambda t: demo_mode.interpret_offline(t))
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.update(create_text=text, create_start=None, create_song="", create_word="",
                            create_medium="Poster", create_audience=None, create_pending=None,
                            create_offer=None, create_message=None)
    create_ui.build_from_input()
    pending = st.session_state.get("create_pending")
    return pending["vector"]["user_query"] if pending else None


def test_create_attaches_cleaned_typed_text(monkeypatch):
    assert _build(monkeypatch, "a velvet poster for Dark Romance, email me@x.com") == \
        "a velvet poster for Dark Romance email"


def test_typed_text_is_never_sent_for_concern_demo_or_offline(monkeypatch):
    assert _build(monkeypatch, "Dark Romance poster but i feel hopeless and worthless lately") in ("", None)
    assert _build(monkeypatch, "a velvet poster for Dark Romance", demo=True) == ""
    assert _build(monkeypatch, "a velvet poster for Dark Romance", online=False) == ""


def test_the_feel_to_create_bridge_sends_no_typed_text():
    import bridge
    result = demo_mode.interpret_offline("I miss my grandmother's kitchen so much")
    vector = bridge.feeling_to_vector(result)
    assert not vector.get("user_query")
    universe = creative.universe(vector, 0.5)
    assert universe["user_query"] == ""


def test_a_missing_key_skips_that_source_politely(monkeypatch, fake_internet):
    monkeypatch.setattr(o, "secret", lambda name: None)
    vector, found, brief = brief_for("Cottagecore")
    out = o.gather(brief, found, creative.style_palette(vector, found), [], [])
    assert out["status"]["unsplash"] == "no key" and out["status"]["lastfm"] == "no key"
    assert {s for s, _ in fake_internet} == {"openverse"}


def test_a_failing_service_never_crashes_create_mode(monkeypatch):
    o._cache.clear()

    def broken(*args, **kwargs):
        raise o.SourceError("unavailable")
    monkeypatch.setattr(o, "get_json", broken)
    monkeypatch.setattr(o, "secret", lambda name: "test-key")
    vector, found, brief = brief_for("Cyberpunk")
    out = o.gather(brief, found, creative.style_palette(vector, found), [], [])
    assert out["images"] == [] and out["tracks"] == [] and out["fonts"] == []
    assert "unavailable" in out["status"].values()


def test_extra_songs_are_checked_filtered_and_not_repeated(fake_internet):
    vector, found, brief = brief_for("Dark Romance")
    curated = [{"title": "Clair de Lune", "artist": "Claude Debussy"}]
    out = o.discover_music(brief, found, curated)
    titles = [t["title"] for t in out["tracks"]]
    assert "Clair de Lune" not in titles
    assert "Party Party" not in titles
    assert out["tracks"][0]["title"] == "Velvet Night" and out["tracks"][0]["verified"]


def test_extra_fonts_come_from_the_categories_the_style_needs(fake_internet):
    _, found, _ = brief_for("Dark Romance")
    out = o.more_fonts(found, ["Playfair Display"])
    families = [f["family"] for f in out["fonts"]]
    assert "Playfair Display" not in families and "Roboto" not in families
    assert "Libre Caslon Text" in families


def test_the_universe_carries_online_results_when_enabled(monkeypatch, fake_internet):
    monkeypatch.setattr(o, "enabled", lambda: True)
    vector, found, brief = brief_for("Dark Romance")
    universe = creative.universe(vector, 0.5)
    assert universe["brief"]["styles"] == ["Dark Romance"]
    assert universe["online"]["images"] and universe["online"]["tracks"]
    import create_ui
    html = create_ui.image_board_html(universe["online"]["images"])
    assert "Unsplash" in html and "CC BY" in html
