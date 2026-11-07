"""Tests for the ORBIT Creative Feature Matching Algorithm (creative_match.py)."""
import pandas as pd
import pytest

import creative
import creative_match as cm
import demo_mode
import fonts
import music
import palette
import vibe

DATA = "data/"


def universe_for(idea):
    result = demo_mode.interpret_offline(idea)
    vector = vibe.build(idea, result["emotions"], match_text=result.get("model_text"))
    return vector, creative.universe(vector, 0.5)


def hue_distance(a, b):
    return abs((a - b + 180) % 360 - 180)


def test_every_name_in_the_style_table_exists_in_orbits_data():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1] / "data"
    aesthetics = set(pd.read_csv(root / "aesthetics.csv")["name"])
    catalogue = pd.read_csv(root / "music_catalog.csv")
    font_tags = {t for x in pd.read_csv(root / "fonts.csv")["tags"] for t in x.split("|")}
    music_tags = {t for x in catalogue["tags"] for t in x.split("|")}
    for style in cm.load_profiles().values():
        assert set(style["aesthetics"]) <= aesthetics, style["name"]
        assert set(style["music_genres"]) <= set(catalogue["genre"]), style["name"]
        assert set(style["font_tags"]) <= font_tags, style["name"]
        assert set(style["music_tags"]) <= music_tags, style["name"]
        assert style["hue"] is not None and style["atmosphere"], style["name"]


def test_a_phrase_uses_up_its_words():
    found = cm.match("Dark Romance")
    assert [s["name"] for s in found["styles"]] == ["Dark Romance"]
    assert found["keywords"] == [("dark romance", "Dark Romance", "phrase", 3)]


def test_dark_on_its_own_names_no_style():
    assert cm.match("a dark night poster") is None
    assert cm.match("my brother's wedding") is None


def test_two_styles_blend_equally_and_plurals_count():
    found = cm.match("Dreamy Nostalgia")
    assert [(s["name"], s["strength"]) for s in found["styles"]] == [("Dreamy", 1.0), ("Nostalgia", 1.0)]
    assert cm.match("a film about dragons")["styles"][0]["name"] == "Fantasy"


def test_a_weak_extra_style_is_dropped():
    found = cm.match("a cyberpunk city with a cute robot")
    assert [s["name"] for s in found["styles"]] == ["Cyberpunk", "Kawaii"]
    found = cm.match("cyberpunk cyberpunk with neon")
    assert [s["name"] for s in found["styles"]] == ["Cyberpunk"]


def test_the_scoring_rules_add_up_as_documented():
    found = cm.match("Dark Romance")
    gothic, _ = cm.item_score(found, "aesthetic", name="Gothic", tags=["dark", "dramatic", "cathedral", "mystery"])
    assert gothic == 1.0
    cyber, _ = cm.item_score(found, "aesthetic", name="Cyberpunk", tags=["neon", "dystopian", "tech", "urban"])
    assert cyber == 0.0
    party, _ = cm.item_score(found, "music", tags=["dance", "celebration"], genre="Bollywood")
    assert party == -0.5
    song, _ = cm.item_score(found, "music", tags=["love", "longing", "calm"], genre="Ghazal")
    assert song == pytest.approx(0.6 * 2 / 3 + 0.4)
    assert cm.final_score(0.5, 1.0) == pytest.approx(0.8)


def test_no_style_means_create_mode_is_unchanged():
    result = demo_mode.interpret_offline("a dark night poster")
    vector = vibe.build("a dark night poster", result["emotions"])
    assert vector["match"] is None
    plain = palette.make_palette(vector["valence"], vector["arousal"], warm=vector["warmth"], bold=vector["bold"],
                                 vintage=-vector["era"], brightness=vector["brightness"])
    assert creative.universe(vector, 0.5)["palette"]["colours"] == plain["colours"]


EXPECTED = {
    "Dark Romance": {"aesthetic": "Gothic", "hue": 345, "font_tags": {"elegant", "romantic", "dramatic", "classic"}},
    "Dark Academia": {"aesthetic": "Dark Academia", "hue": 25, "font_tags": {"literary", "bookish", "classic"}},
    "Cottagecore": {"aesthetic": "Cottagecore", "hue": 100, "font_tags": {"handwritten", "cosy", "soft", "gentle"}},
    "Cyberpunk": {"aesthetic": "Cyberpunk", "hue": 300, "font_tags": {"tech", "sci-fi", "futuristic", "neon"}},
    "Dreamy Nostalgia": {"aesthetic": "Impressionism", "hue": 280, "font_tags": {"soft", "delicate", "vintage",
                                                                                 "romantic", "classic"}},
    "Minimalist Luxury": {"aesthetic": "Minimalism", "hue": 30, "font_tags": {"minimal", "clean", "elegant",
                                                                              "modern", "thin"}},
    "Ethereal Fantasy": {"aesthetic": "Art Nouveau", "hue": 250, "font_tags": {"elegant", "delicate", "romantic",
                                                                               "classic"}},
}


@pytest.mark.parametrize("idea", list(EXPECTED))
def test_each_idea_gets_recommendations_in_its_creative_direction(idea):
    expected = EXPECTED[idea]
    vector, universe = universe_for(idea)
    names = [a["name"] for a in universe["aesthetics"]]
    assert expected["aesthetic"] in names
    assert all(a["fits"] for a in universe["aesthetics"])
    palette_names = {c["name"] for c in universe["palette"]["colours"]}
    style_names = {name for name, _ in cm.anchors(vector["match"])}
    assert universe["palette"]["rule"] == "style colour story" and palette_names <= style_names
    heading = fonts.load_fonts().set_index("family").loc[universe["fonts"]["heading"], "tag_list"]
    assert set(heading) & expected["font_tags"]
    assert sum(bool(t.get("idea_fits")) for t in universe["music"]) >= 6


def test_dark_romance_is_not_horror_or_sad_party_music():
    vector, universe = universe_for("Dark Romance")
    assert not {"Cyberpunk", "Expressionism"} & {a["name"] for a in universe["aesthetics"]}
    for track in universe["music"]:
        assert not {"grief", "dance", "celebration", "playful", "fun"} & set(track["tag_list"]), track["title"]


def test_dark_romance_and_dark_academia_are_now_different():
    _, romance = universe_for("Dark Romance")
    _, academia = universe_for("Dark Academia")
    assert romance["aesthetics"][0]["name"] != academia["aesthetics"][0]["name"]
    assert romance["palette"]["hue"] != academia["palette"]["hue"]


def test_why_lines_name_the_matched_characteristics():
    _, universe = universe_for("Cottagecore")
    assert universe["aesthetics"][0]["why"].startswith("Fits your idea")
    assert any(t["reason"].startswith("Fits your idea's style") for t in universe["music"])
    assert "Cottagecore" in cm.summary(cm.match("Cottagecore"))
