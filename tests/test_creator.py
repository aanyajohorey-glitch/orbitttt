"""Creator Mode: crisis bypass, the Vibe Vector, the Creative Universe, the Spark path."""
import itertools
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import brief
import creative
import fonts
import palette
import spark
import storage
import vibe

APP = str(Path(__file__).resolve().parents[1] / "app.py")
IDEA = "a short film about a rainy Sunday cafe in Mumbai, nostalgic and warm"
EMOTIONS = [("joy", 0.3), ("sadness", 0.3), ("neutral", 0.2)]


@pytest.fixture
def app():
    storage.delete_everything()
    storage.set_setting("onboarded", "1")
    storage.set_setting("demo_mode", "1")        # no emotion model needed
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    at.button(key="mode_Create").click().run()
    return at


def bodies(at):
    return [h.proto.body for h in at.get("html")]


# ---------------------------------------------------------------- crisis runs first in Create too
def test_mode_choice_is_remembered(app):
    assert app.session_state.page == "Create"
    assert storage.get_setting("last_mode") == "Create"


def test_crisis_idea_shows_only_help_and_generates_nothing(app):
    app.text_area(key="create_text").input("i want to end my life").run()
    app.button(key="create_go").click().run()
    assert any("14416" in b for b in bodies(app))
    assert app.session_state.creative is None and not app.get("download_button")
    assert "create_text" not in app.session_state or not app.session_state.create_text   # not kept


def test_crisis_word_in_spark_bypasses_the_ideas(app):
    app.button(key="create_spark").click().run()
    for step in range(1, 7):
        app.button(key=f"spark_skip_{step}").click().run()
    app.text_input(key="spark_word").input("suicide").run()
    app.button(key="spark_finish").click().run()
    assert any("14416" in b for b in bodies(app))
    assert "spark_ideas" not in app.session_state or not app.session_state.spark_ideas
    assert app.session_state.creative is None


def test_a_normal_idea_builds_a_universe(app):
    app.text_area(key="create_text").input(IDEA).run()
    app.button(key="create_go").click().run()
    if app.session_state.create_pending:
        app.button(key="cq_skip").click().run()
    assert not app.exception and app.session_state.creative
    assert len(app.get("download_button")) == 4


# ---------------------------------------------------------------- the Vibe Vector and the universe
def test_vibe_words_are_understood():
    v = vibe.build(IDEA, EMOTIONS)
    assert {"rainy", "cafe", "nostalgic"} <= set(v["themes"])
    assert v["era"] < 0 and v["texture"] > 0          # nostalgic -> vintage, hand-made


def test_universe_is_complete_and_deterministic():
    v = vibe.build(IDEA, EMOTIONS, medium="Film")
    a, b = creative.universe(v), creative.universe(v)
    assert a["concept"] == b["concept"] and a["palette"] == b["palette"]
    assert all(palette.is_valid_hex(c["hex"]) for c in a["palette"]["colours"]) and len(a["palette"]["colours"]) == 5
    assert len(a["aesthetics"]) == 3 and len(a["music"]) == 8 and len(a["creators"]) == 6
    assert len({c["name"] for c in a["creators"]}) == 6
    assert any("India" in c["region"] for c in a["creators"])
    assert all(c["why"] for c in a["creators"]) and all(x["why"] for x in a["aesthetics"])


def test_fonts_come_from_the_csv():
    families = set(fonts.load_fonts()["family"])
    pair = fonts.pair(0.5, -0.5, -0.5)
    assert pair["heading"] in families and pair["body"] in families and pair["heading"] != pair["body"]
    assert fonts.pair(0.3, 0, 0, hindi=True)["heading"] == "Tiro Devanagari Hindi"


@pytest.mark.parametrize("chip", list(vibe.CHIPS))
def test_every_refine_chip_changes_the_universe(chip):
    v = vibe.build(IDEA, EMOTIONS, medium="Film")
    before = creative.universe(v)
    after = creative.universe(vibe.refine(v, chip))
    assert after["palette"] != before["palette"] or after["aesthetics"] != before["aesthetics"] or \
        after["vector"]["themes"] != before["vector"]["themes"]


def test_locked_elements_stay_the_same():
    v = vibe.build(IDEA, EMOTIONS, medium="Film")
    first = creative.universe(v)
    second = creative.universe(vibe.refine(v, "Bolder"), locks={"palette", "creators"}, previous=first)
    assert second["palette"] == first["palette"] and second["creators"] == first["creators"]
    unlocked = creative.universe(vibe.refine(v, "Bolder"))
    assert unlocked["palette"] != first["palette"]


def test_three_directions_differ():
    v = vibe.build(IDEA, EMOTIONS, medium="Film")
    universes = {name: creative.universe(d) for name, d in vibe.directions(v).items()}
    palettes = {name: tuple(c["hex"] for c in u["palette"]["colours"]) for name, u in universes.items()}
    assert len(set(palettes.values())) == 3


def test_discovery_reaches_less_known_creators():
    v = vibe.build(IDEA, EMOTIONS, medium="Film")
    familiar = creative.rank_creators(v, discovery=0.0)
    unfamiliar = creative.rank_creators(v, discovery=1.0)
    level = lambda rows: sum(r["mainstream_level"] for r in rows) / len(rows)   # noqa: E731
    assert level(unfamiliar) < level(familiar)


def test_brief_is_a_pdf():
    v = vibe.build(IDEA, EMOTIONS, medium="Film")
    assert brief.pdf(creative.universe(v))[:5] == b"%PDF-"


# ---------------------------------------------------------------- the Spark path
FULL = {"medium": "Film", "emotions": ["Nostalgia", "Love"], "setting": "a grandmother's kitchen",
        "era": "Retro (1980s-2000s)", "contrast": "lonely + warm", "texture": "film grain", "word": "monsoon"}
QUESTION_KEYS = ["medium", "emotions", "setting", "era", "contrast", "texture"]


@pytest.mark.parametrize("skipped", [combo for n in range(7) for combo in itertools.combinations(QUESTION_KEYS, n)])
def test_every_skip_path_still_gives_three_ideas(skipped):
    answers = {k: v for k, v in FULL.items() if k not in skipped}
    ideas = spark.three_ideas(answers)
    assert [i["direction"] for i in ideas] == ["Safe", "Bold", "Weird"]
    assert all(i["title"] and i["logline"] and i["why"] for i in ideas)
    assert len({i["title"] for i in ideas}) == 3


def test_safe_idea_keeps_every_answer_and_quotes_it():
    safe = spark.three_ideas(FULL)[0]
    for key in ("medium", "setting", "contrast", "texture"):
        assert safe[key] == FULL[key]
    assert "grandmother's kitchen" in safe["why"] and "monsoon" in safe["why"]


@pytest.mark.parametrize("element", spark.ELEMENTS)
def test_remix_changes_only_the_chosen_element(element):
    idea = spark.three_ideas({"emotions": ["Wonder"]})[0]
    new = spark.remix(idea, element, {"emotions": ["Wonder"]})
    assert new[element] != idea[element]
    assert all(new[k] == idea[k] for k in spark.ELEMENTS if k != element)


@pytest.mark.parametrize("element", spark.ELEMENTS)
def test_lock_keeps_the_chosen_element_and_changes_the_rest(element):
    idea = spark.three_ideas({"emotions": ["Thrill"]})[1]
    new = spark.lock(idea, element, {"emotions": ["Thrill"]})
    assert new[element] == idea[element]
    assert all(new[k] != idea[k] for k in spark.ELEMENTS if k != element)


def test_heavy_choices_only_mention_feel_mode():
    assert spark.heavy({"emotions": ["Grief"]}) and spark.heavy({"feeling_now": "Very low"})
    assert not spark.heavy({"emotions": ["Joy", "Calm"]})


def test_an_idea_becomes_a_universe():
    idea = spark.three_ideas(FULL)[0]
    universe = creative.universe(spark.to_vector(idea, FULL))
    assert universe["vector"]["medium"] == "Film" and universe["vector"]["era"] == spark.ERAS[FULL["era"]]
