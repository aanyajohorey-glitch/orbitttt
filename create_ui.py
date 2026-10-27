"""
create_ui.py
The Create tab (Creator Mode).

Flow:  big input box (+ optional chips)  ->  silent crisis check  ->  Vibe Vector
       ->  at most 3 tappable clarifying questions (skippable)  ->  Creative Universe
       ->  refine chips, sliders, locks, three directions, version history, exports.
"I don't have an idea yet" opens the Spark path (spark_ui.py).

Crisis rule: if any text typed here contains crisis wording, ONLY the safety
response is shown: nothing is generated, and the text is not kept.
"""
import colorsys
import copy
from datetime import date, datetime
from urllib.parse import quote_plus

import streamlit as st

import brief
import bridge
import creative
import fonts as fontlib
import games
import music
import palette
import spark
import theme
import vibe
from components import esc, go_to, note, section_header
from explain import highlight_html, importance_of
from safety import check as safety_check
from safety import safety_card_html
from studio import moodboard_html

AUDIENCES = ["Friends", "Teenagers", "Kids", "Everyone", "A client"]
START_FROM = ["A feeling", "A colour", "A song", "A word"]
HISTORY_SIZE = 10
MEDIUM_HINTS = {"film": "Film", "movie": "Film", "documentary": "Film", "book": "Book", "story": "Book",
                "novel": "Book", "poems": "Book", "comic": "Book", "brand": "Brand", "logo": "Brand",
                "shop": "Brand", "poster": "Poster", "posters": "Poster", "video": "Music video",
                "song": "Music video", "app": "App", "website": "App", "game": "App"}
DIRECTION_HINTS = {"Safe": "your vibe, familiar picks", "Bold": "louder, stronger, braver",
                   "Weird": "flipped and unexpected"}


# ---------------------------------------------------------------
# Safety and analysis
# ---------------------------------------------------------------
def crisis_in(*texts):
    return any(t and safety_check(t) == "crisis" for t in texts)


def block():
    """Crisis: show only help, and forget the text."""
    st.session_state.create_blocked = True
    for key in ("create_text", "create_song", "create_word", "spark_word"):
        st.session_state.pop(key, None)
    st.session_state.creative = None
    theme.reset_world()                     # calm, neutral colours while help is shown


def read_emotions(text):
    """The emotion blend for the idea (ORBIT's model, or the offline estimate in demo mode).
    Nothing is saved: Creator Mode is not a journal check-in."""
    import demo_mode
    from analysis import interpret
    try:
        result = demo_mode.interpret_offline(text) if demo_mode.enabled() else interpret(text)
    except Exception:
        st.session_state.model_failed = True
        result = demo_mode.interpret_offline(text)
    return result


def colour_to_vibe(hex_colour):
    """A starting colour -> warmth, brightness and boldness (hue, lightness, saturation)."""
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    hue = h * 360
    warmth = 1.0 if hue < 70 or hue > 330 else -1.0 if 170 < hue < 260 else 0.2
    return {"warmth": warmth * s, "brightness": vibe.clamp((l - 0.5) * 2), "bold": vibe.clamp((s - 0.4) * 2)}


# ---------------------------------------------------------------
# Generating and storing versions
# ---------------------------------------------------------------
def state():
    return st.session_state.get("creative")


def generate(vector, discovery=None, label="New idea"):
    """Make a universe from a vector; the previous version goes into the history."""
    current = state()
    locks = set(st.session_state.get("create_locks", set()))
    previous = current["universe"] if current else None
    universe = creative.universe(vector, discovery, locks=locks, previous=previous)
    history = (current["history"] if current else [])
    if current:
        history = ([{"label": current["label"], "time": current["time"], "universe": current["universe"]}]
                   + history)[:HISTORY_SIZE]
    st.session_state.creative = {"universe": universe, "label": label, "history": history,
                                 "time": datetime.now().strftime("%H:%M:%S")}
    theme.set_vibe_world(universe)          # the whole app takes on this universe's colours


def restore(index):
    current = state()
    old = current["history"][index]
    history = [{"label": current["label"], "time": current["time"], "universe": current["universe"]}] + \
        [h for i, h in enumerate(current["history"]) if i != index]
    st.session_state.creative = {"universe": old["universe"], "label": f"Restored: {old['label']}",
                                 "history": history[:HISTORY_SIZE], "time": datetime.now().strftime("%H:%M:%S")}
    theme.set_vibe_world(old["universe"])


def apply_chip(chip):
    universe = state()["universe"]
    generate(vibe.refine(universe["vector"], chip), universe["discovery"], label=chip)


def apply_direction(name):
    universe = state()["universe"]
    base = {k: v for k, v in universe["vector"].items() if k not in ("direction", "discovery", "harmony")}
    chosen = vibe.directions(base)[name]
    generate(chosen, chosen["discovery"], label=f"{name} direction")


def apply_sliders():
    universe = state()["universe"]
    s = st.session_state
    vector = vibe.with_sliders(universe["vector"], s.cs_warm, s.cs_energy, s.cs_bold, s.cs_era, s.cs_bright)
    generate(vector, s.cs_discovery, label="Fine-tuned")


def new_idea():
    st.session_state.creative = None
    st.session_state.create_pending = None
    st.session_state.create_locks = set()


# ---------------------------------------------------------------
# 1. Entry screen
# ---------------------------------------------------------------
def build_from_input():
    s = st.session_state
    text = s.get("create_text", "").strip()
    start = s.get("create_start")
    song, word = s.get("create_song", ""), s.get("create_word", "")
    if crisis_in(text, song, word):
        block()
        return
    extra = " ".join(x for x in (song, word) if x)
    full = " ".join(x for x in (text, extra) if x).strip()
    if not full and not (start == "A feeling" and s.get("create_feeling")) and start != "A colour":
        st.session_state.create_message = "Write a few words about your idea first, or try “I don't have an idea yet”."
        return
    result = read_emotions(full or "a new creative idea")
    emotions = result["emotions"]
    if start == "A feeling" and s.get("create_feeling"):
        chosen = [spark.EMOTIONS[f] for f in s["create_feeling"][:2]]
        emotions = [(e[2], 1.0 / len(chosen)) for e in chosen] + [(l, sc * 0.3) for l, sc in emotions[:3]]
    vector = vibe.build(full or "a new creative idea", emotions, medium=s.get("create_medium"),
                        audience=s.get("create_audience"), start_from=start,
                        match_text=result.get("model_text"))
    if start == "A colour" and s.get("create_colour"):
        vector.update({k: round(v, 3) for k, v in colour_to_vibe(s["create_colour"]).items()})
    vector["result"] = {k: result[k] for k in ("text", "model_text", "final", "translated")}
    st.session_state.create_offer = bridge.offer_for(full)       # stress or creative-block words?
    vector["concern"] = result.get("safety") == "concern"
    if not vector["medium"]:                     # "a short film about..." already says the medium
        words = vibe.words_in(result.get("model_text") or full)
        vector["medium"] = next((MEDIUM_HINTS[w] for w in words if w in MEDIUM_HINTS), None)
    # Up to 3 tappable questions when something is unclear.
    questions = []
    if not vector["medium"]:
        questions.append("medium")
    if result["final"].get("unsure") or emotions[0][0] == "neutral":
        questions.append("feeling")
    if not any(w in vibe.ERA_WORDS for w in vibe.words_in(result.get("model_text") or full)):
        questions.append("era")
    st.session_state.create_pending = {"vector": vector, "questions": questions[:3]}
    if not questions:
        finish_questions(skip=True)            # nothing to ask: straight to the universe


def entry_screen():
    section_header("Create", "What are you making, or what's on your mind?", first=True)
    with st.container(key="glass-create-input"):
        st.text_area("Your idea", key="create_text", height=150, label_visibility="collapsed",
                     placeholder="e.g. a short film about a rainy Sunday café in Mumbai, nostalgic and warm")
        st.pills("Medium (optional)", spark.MEDIUMS, key="create_medium")
        st.pills("Audience (optional)", AUDIENCES, key="create_audience")
        start = st.pills("Start from (optional)", START_FROM, key="create_start")
        if start == "A feeling":
            st.pills("Which feeling? (up to 2)", list(spark.EMOTIONS), selection_mode="multi", key="create_feeling")
        elif start == "A colour":
            st.color_picker("Pick a colour", "#C9B9E8", key="create_colour")
        elif start == "A song":
            st.text_input("A song title (just the name, no lyrics)", key="create_song", max_chars=80)
        elif start == "A word":
            st.text_input("One word", key="create_word", max_chars=30)
        left, right = st.columns([1, 1])
        left.button("Build my universe", type="primary", key="create_go", on_click=build_from_input,
                    width="stretch")
        right.button("I don't have an idea yet", key="create_spark", on_click=spark_start, width="stretch")
    message = st.session_state.pop("create_message", None)
    if message:
        st.warning(message)
    note("Nothing you type here is saved unless you download it. Creator Mode isn't a journal check-in.")


def spark_start():
    st.session_state.spark_step = 1
    st.session_state.spark_answers = {}
    st.session_state.spark_ideas = None


# ---------------------------------------------------------------
# 2. Clarifying questions (tappable, skippable)
# ---------------------------------------------------------------
def finish_questions(skip=False):
    pending = st.session_state.create_pending
    vector = pending["vector"]
    s = st.session_state
    if not skip:
        if s.get("cq_medium"):
            vector["medium"] = s.cq_medium
        if s.get("cq_feeling"):
            chosen = [spark.EMOTIONS[f] for f in s.cq_feeling[:2]]      # "up to 2"
            vector["valence"] = round(sum(e[0] for e in chosen) / len(chosen), 3)
            vector["arousal"] = round(sum(e[1] for e in chosen) / len(chosen), 3)
            vector["emotions"] = [(e[2], 1.0 / len(chosen)) for e in chosen] + vector["emotions"][:3]
        if s.get("cq_era"):
            vector["era"] = spark.ERAS[s.cq_era]
    st.session_state.create_pending = None
    generate(vector, 0.5, label="First version")


def questions_screen():
    pending = st.session_state.create_pending
    section_header("Create", "A couple of quick taps", "Optional: they help ORBIT get the vibe right.", first=True)
    with st.container(key="glass-create-questions"):
        if "medium" in pending["questions"]:
            st.pills("What is it?", spark.MEDIUMS, key="cq_medium")
        if "feeling" in pending["questions"]:
            st.pills("Which feeling should it have? (up to 2)", list(spark.EMOTIONS), selection_mode="multi",
                     key="cq_feeling")
        if "era" in pending["questions"]:
            st.pills("When does it live?", list(spark.ERAS), key="cq_era")
        left, right = st.columns(2)
        left.button("Continue", type="primary", key="cq_go", on_click=finish_questions, width="stretch")
        right.button("Skip", key="cq_skip", on_click=finish_questions, args=(True,), width="stretch")


# ---------------------------------------------------------------
# The bridge to Feel: a short break, then back to the project
# ---------------------------------------------------------------
def take_break(kind, game=None, block=None):
    st.session_state.create_break = {"kind": kind, "game": game, "block": block}
    st.session_state.create_offer = None


def end_break():
    st.session_state.create_break = None          # the project in session state is untouched


def check_in_on_project():
    """'How's the project going?' Crisis first, then stress / block words."""
    text = st.session_state.get("cu_feel", "").strip()
    if not text:
        return
    if crisis_in(text):
        block()
        return
    st.session_state.cu_feel = ""
    offer = bridge.offer_for(text)
    if offer:
        st.session_state.create_offer = offer
    else:
        st.session_state.flash.append("Sounds like it's going okay. Keep going!")


def stuck():
    st.session_state.create_offer = bridge.offer_for("I'm stuck")


def offer_card(offer):
    with st.container(key="glass-cu-offer"):
        what = (f"a bit of <b>{esc(offer['block'].lower())}</b>" if offer["block"] else "some stress")
        st.html(f'<div class="eyebrow">A short break?</div><p class="body">It sounds like there might be {what} in '
                "the way. That's very normal in creative work. Want to step away for a few minutes? Your project "
                "will be right here when you come back.</p>")
        cols = st.columns(4 if offer["block"] else 3)
        cols[0].button("2-minute breather", key="br_breathe", on_click=take_break, args=("game", "orb_flow"),
                       width="stretch")
        cols[1].button(f"Play {games.GAMES[offer['game']][0]}", key="br_game", on_click=take_break,
                       args=("game", offer["game"]), width="stretch")
        if offer["block"]:
            cols[2].button(f"{offer['block']} exercise", key="br_exercise", on_click=take_break,
                           args=("exercise", None, offer["block"]), width="stretch")
        cols[-1].button("No thanks", key="br_no", type="tertiary", width="stretch",
                        on_click=lambda: st.session_state.update(create_offer=None))


def break_screen(pause):
    title = games.GAMES[pause["game"]][0] if pause["kind"] == "game" else f"{pause['block']}: a 5-minute exercise"
    section_header("A short break", title, "Your project is saved in this session. Come back whenever you're ready.",
                   first=True)
    if pause["kind"] == "game":
        with st.container(key="glass-break-game"):
            games.play(pause["game"], None, height=600)
    else:
        with st.container(key="glass-break-exercise"):
            st.html(f'<p class="cu-vision">{esc(bridge.BLOCKS[pause["block"]]["exercise"])}</p>'
                    '<p class="body">No need to show anyone. When the five minutes are up, come back.</p>')
    from feedback_ui import thumbs
    thumbs("tool", f"Create break · {title}", key=f"fb_break_{title}", label="Did the break help?")
    st.button("Back to my project", key="br_back", type="primary", on_click=end_break)


# ---------------------------------------------------------------
# 3. The Creative Universe
# ---------------------------------------------------------------
def lock_toggle(element):
    locks = st.session_state.setdefault("create_locks", set())
    key = f"lock_{element}"

    def flip():
        (locks.add if st.session_state[key] else locks.discard)(element)
    st.toggle("Lock", key=key, value=element in locks, on_change=flip,
              help="A locked part stays the same when you refine or change direction.")


def section(element, eyebrow):
    left, right = st.columns([5, 1], vertical_alignment="center")
    left.html(f'<div class="eyebrow">{esc(eyebrow)}</div>')
    with right:
        lock_toggle(element)


def palette_rows(result):
    swatches = "".join(
        f'<div class="cu-swatch"><span style="background:{c["hex"]}"></span><b>{esc(c["name"])}</b>'
        f'<small>{c["hex"]} · {esc(c["role"])}</small></div>' for c in result["colours"])
    checks = "".join(
        f'<div class="check-row"><span>{esc(c["pair"])}</span><span>{c["ratio"]} : 1 (needs {c["needed"]})</span>'
        f'<b>{"Pass" if c["passes"] else "Decoration only"}</b></div>' for c in result["checks"])
    return f'<div class="cu-swatches">{swatches}</div><div style="margin-top:.6rem">{checks}</div>'


def how_it_was_made(universe):
    vector, result = universe["vector"], universe["palette"]
    words = vibe.describe(vector)
    rows = "".join(f'<div class="check-row"><span>{esc(k)}</span><span>{vector[key]:+.2f}</span><b>{esc(v)}</b></div>'
                   for (k, v), key in zip(words.items(), ["valence", "arousal", "brightness", "warmth", "era",
                                                          "texture", "bold"]))
    st.html('<p class="body"><b>The Vibe Vector</b>: every output below is generated from these numbers.</p>'
            + rows + f'<p class="body" style="margin-top:.6rem">Understood words: '
            f'{esc(", ".join(vector["themes"]) or "none")}. Emotions: '
            + esc(", ".join(f"{l} {s:.0%}" for l, s in vector["emotions"][:4])) + ".</p>"
            f'<p class="body"><b>Palette:</b> the feeling\'s angle on the valence-energy circle gives hue '
            f'{result["hue"]}°, energy and strength give saturation {result["saturation"]}, light gives lightness '
            f'{result["lightness"]}; harmony rule <b>{result["rule"]}</b>; ink darkened until WCAG AA passes.</p>'
            f'<p class="body"><b>Typography:</b> {esc(universe["fonts"]["why"])}</p>'
            '<p class="body"><b>Aesthetics, music and creators:</b> cosine similarity between the Vibe Vector and '
            "each item's numbers plus shared tags, then Maximal Marginal Relevance so the list stays varied. The "
            f'discovery dial ({universe["discovery"]:.1f}) moves from familiar to unfamiliar.</p>')
    importance = importance_of(vector["result"]) if vector.get("result") and vector["result"].get("final") else None
    if importance:
        st.html('<div class="field-label" style="margin-top:.6rem">Which words drove the emotion reading</div>'
                + highlight_html(importance))


def orbit_html(universe):
    """The idea at the centre; palette, type, music, artists and aesthetics orbit around it as planets.
    Refining regenerates the universe, so these planets update straight away."""
    colours = [c["hex"] for c in universe["palette"]["colours"]]
    fonts_used, concept = universe["fonts"], universe["concept"]
    planets = [
        ("Palette", f'<i class="op-swatch" style="background:conic-gradient({", ".join(colours[:3] + colours[:1])})">'
                    "</i>", universe["palette"]["colours"][0]["name"]),
        ("Type", f'<i class="op-type" style="font-family:\'{fonts_used["heading"]}\',serif">Aa</i>',
         fonts_used["heading"]),
        ("Music", '<i class="op-icon">♪</i>', universe["music"][0]["title"] if universe["music"] else ""),
        ("Artists", '<i class="op-icon">✦</i>', universe["creators"][0]["name"] if universe["creators"] else ""),
        ("Aesthetic", '<i class="op-icon">◐</i>', universe["aesthetics"][0]["name"] if universe["aesthetics"] else ""),
    ]
    items = "".join(
        f'<div class="op-planet" style="--a:{i * 72}deg"><div class="op-body">{icon}<b>{esc(label)}</b>'
        f"<small>{esc(detail)}</small></div></div>" for i, (label, icon, detail) in enumerate(planets))
    return (f'<div class="uorbit" style="--c1:{colours[0]};--c2:{colours[1]}"><div class="uorbit-ring"></div>'
            f'<div class="uorbit-spin">{items}</div><div class="uorbit-core">'
            f'<span style="font-family:\'{fonts_used["heading"]}\',serif">{esc(concept["title"])}</span></div></div>')


def universe_screen():
    data = state()
    universe = data["universe"]
    vector, concept = universe["vector"], universe["concept"]
    fonts_used = universe["fonts"]
    st.html("<style>" + fontlib.google_fonts_css(*fontlib.families_in(fonts_used)) + "</style>")

    st.html(orbit_html(universe))
    with st.container(key="glass-cu-concept"):
        section("concept", f"Your creative universe · {data['label']}"
                + (f" · {vector['direction']}" if vector.get("direction") else ""))
        st.html(f'<div class="cu-title" style="font-family:\'{fonts_used["heading"]}\',serif">{esc(concept["title"])}</div>'
                f'<p class="cu-vision" style="font-family:\'{fonts_used["body"]}\',sans-serif">{esc(concept["vision"])}</p>'
                + ('<span class="badge">Polished with AI · checked</span>' if concept.get("polished") else ""))
        a, b, c = st.columns(3)
        a.button("New idea", key="cu_new", on_click=new_idea, width="stretch")
        import llm
        if llm.active_mode() != "templates" and not concept.get("polished"):
            b.button("Polish the vision with AI", key="cu_polish", on_click=polish, width="stretch")
    if st.session_state.get("create_offer"):
        offer_card(st.session_state.create_offer)
    with st.container(key="glass-cu-feel"):
        left, middle, right = st.columns([3, 1, 1], vertical_alignment="bottom")
        left.text_input("How's the project going?", key="cu_feel", max_chars=200,
                        placeholder="e.g. it has to be perfect and I can't start")
        middle.button("Tell ORBIT", key="cu_feel_go", on_click=check_in_on_project, width="stretch")
        right.button("I'm stuck", key="cu_stuck", on_click=stuck, width="stretch")
    if vector.get("concern"):
        note("Some of what you wrote sounds heavy. Making things can help, and so can talking: the <b>Feel</b> tab "
             "is here whenever you want it, and Tele-MANAS (14416) is free, any time.")

    with st.container(key="glass-cu-refine"):
        st.html('<div class="eyebrow">Refine the vibe</div>')
        chips = list(vibe.CHIPS.items())
        for row in (chips[:3], chips[3:]):                         # two rows of three, so labels fit
            for col, (chip, help_text) in zip(st.columns(3), row):
                col.button(chip, key=f"chip_{chip}", on_click=apply_chip, args=(chip,), help=help_text,
                           width="stretch")
        with st.expander("Sliders and discovery dial"):
            left, right = st.columns(2)
            left.slider("Warm ↔ Cool", -1.0, 1.0, 0.0, 0.1, key="cs_warm")
            right.slider("Calm ↔ Energetic", -1.0, 1.0, 0.0, 0.1, key="cs_energy")
            left.slider("Soft ↔ Bold", -1.0, 1.0, 0.0, 0.1, key="cs_bold")
            right.slider("Vintage ↔ Modern", -1.0, 1.0, 0.0, 0.1, key="cs_era")
            left.slider("Dark ↔ Bright", -1.0, 1.0, 0.0, 0.1, key="cs_bright")
            right.slider("Comfort zone ↔ Unfamiliar", 0.0, 1.0, float(universe["discovery"]), 0.1, key="cs_discovery",
                         help="Unfamiliar picks lesser-known creators, aesthetics and music.")
            st.button("Apply", key="cs_apply", on_click=apply_sliders, type="primary")

    st.html('<div class="eyebrow" style="margin:1rem 0 .4rem">Three directions</div>')
    base = {k: v for k, v in vector.items() if k not in ("direction", "discovery", "harmony")}
    for col, (name, option) in zip(st.columns(3), vibe.directions(base).items()):
        preview = palette.make_palette(option["valence"], option["arousal"], warm=option["warmth"], bold=option["bold"],
                                       vintage=-option["era"], harmony=option["harmony"],
                                       brightness=option["brightness"])
        strip = "".join(f'<i style="background:{c["hex"]}"></i>' for c in preview["colours"])
        with col:
            with st.container(key=f"glass-dir-{name}"):
                st.html(f'<div class="dir-card"><b>{name}</b><div class="dir-strip">{strip}</div>'
                        f'<small>{DIRECTION_HINTS[name]}</small></div>')
                st.button(f"Use {name}", key=f"dir_{name}", on_click=apply_direction, args=(name,), width="stretch")

    with st.container(key="glass-cu-palette"):
        section("palette", "Palette and moodboard")
        tiles = universe["moodboard"]["textures"]
        st.html(moodboard_html(universe["palette"], fonts_used, tiles, universe["moodboard"]["keywords"]))
        st.html(f'<p class="body" style="margin-top:.6rem">Lighting: <b>{esc(universe["moodboard"]["lighting"])}</b>. '
                f'Textures: {esc(", ".join(tiles))}.</p>' + palette_rows(universe["palette"]))
        lock_line = st.columns([5, 1])[1]
        with lock_line:
            lock_toggle("moodboard")

    with st.container(key="glass-cu-type"):
        section("fonts", "Typography")
        st.html(f'<div class="cu-type"><div style="font-family:\'{fonts_used["heading"]}\',serif;font-size:2.2rem">'
                f'{esc(concept["title"])}</div><p style="font-family:\'{fonts_used["body"]}\',sans-serif">'
                f'{esc(fonts_used["heading"])} for headings and {esc(fonts_used["body"])} for text: '
                f'{esc(fonts_used["feel"])}. Both are free Google Fonts.</p></div>')
        st.html('<div class="field-label" style="margin-top:1rem">Your fonts, and more ideas for this vibe</div>'
                + fontlib.gallery_html(fonts_used, concept["title"]))

    with st.container(key="glass-cu-aesthetics"):
        section("aesthetics", "Aesthetics to explore")
        st.html('<div class="cu-cards">' + "".join(
            f'<div class="cu-card"><b>{esc(a["name"])}</b><small>{esc(a["era_label"])} · {esc(a["origin"])}</small>'
            f'<p class="body">{esc(a["why"])}</p></div>' for a in universe["aesthetics"]) + "</div>")

    with st.container(key="glass-cu-music"):
        section("music", "Music to work to")
        rows = []
        for i, track in enumerate(universe["music"], 1):
            spotify, youtube = music.links(track)
            rows.append(f'<div class="track"><span class="track-num">{i:02d}</span><div><b>{esc(track["title"])}</b> · '
                        f'{esc(track["artist"])}<small>{esc(track["language"])} · {esc(track["genre"])}</small>'
                        f'<p class="body">{esc(track["reason"])}</p></div><div class="track-links">'
                        f'<a href="{spotify}" target="_blank" rel="noopener">Spotify</a>'
                        f'<a href="{youtube}" target="_blank" rel="noopener">YouTube</a></div></div>')
        st.html("".join(rows))

    with st.container(key="glass-cu-creators"):
        section("creators", "Creators and artists to discover")
        st.html('<div class="cu-cards">' + "".join(
            f'<div class="cu-card"><b>{esc(c["name"])}</b><small>{esc(c["field"])} · {esc(c["region"])}</small>'
            f'<p class="body">{esc(c["why"])}</p><a href="https://www.google.com/search?q='
            f'{quote_plus(c["name"] + " " + c["field"])}" target="_blank" rel="noopener">Look them up</a></div>'
            for c in universe["creators"]) + "</div>")

    with st.expander("How this was made"):
        how_it_was_made(universe)

    ratings_panel(universe)

    with st.container(key="glass-cu-export"):
        st.html('<div class="eyebrow">Export</div>')
        name = f"orbit_brief_{date.today()}"
        a, b, c, d = st.columns(4)
        a.download_button("Creative brief (PDF)", brief.pdf(universe), file_name=f"{name}.pdf",
                          mime="application/pdf", width="stretch")
        b.download_button("Moodboard (PNG)", palette.png_board(universe["palette"], fonts_used,
                          universe["moodboard"]["keywords"]), file_name=f"{name}.png", mime="image/png",
                          width="stretch")
        c.download_button("Palette (CSS)", palette.css_variables(universe["palette"]), file_name=f"{name}.css",
                          mime="text/css", width="stretch")
        d.download_button("Palette (JSON)", palette.as_json(universe["palette"], fonts_used,
                          {"title": concept["title"]}), file_name=f"{name}.json", mime="application/json",
                          width="stretch")

    if data["history"]:
        with st.expander(f"Version history ({len(data['history'])})"):
            for i, item in enumerate(data["history"]):
                left, right = st.columns([4, 1], vertical_alignment="center")
                strip = "".join(f'<i style="background:{c["hex"]}"></i>' for c in item["universe"]["palette"]["colours"])
                left.html(f'<div class="hist-row"><div class="dir-strip">{strip}</div><b>'
                          f'{esc(item["universe"]["concept"]["title"])}</b><small>{esc(item["label"])} · '
                          f'{item["time"]}</small></div>')
                right.button("Restore", key=f"restore_{i}", on_click=restore, args=(i,), width="stretch")


def ratings_panel(universe):
    """Ratings for the AI Lab: palette fit, cohesion, music relevance (1-5), precision@k and novelty."""
    from feedback_ui import save_count
    from studio import save_stars
    sig = (universe["concept"]["title"] + state()["time"]).replace(" ", "_")
    with st.container(key="glass-cu-ratings"):
        st.html('<div class="eyebrow">Rate this universe (helps ORBIT improve)</div>')
        cols = st.columns(3)
        for col, (kind, question) in zip(cols, [("creative_palette", "Does the palette fit your idea?"),
                                               ("creative_cohesion", "Does it all feel like one world?"),
                                               ("creative_music", "Does the music fit the project?")]):
            with col:
                st.html(f'<span class="feedback-label">{question}</span>')
                key = f"fb_{kind}_{sig}"
                st.feedback("stars", key=key, on_change=save_stars, args=(kind, universe["vector"].get(
                    "direction", "Default"), key))
        titles = [t["title"] for t in universe["music"]]
        st.pills("Tracks that fit your project (tap all that do)", titles, selection_mode="multi",
                 key=f"fb_p8_{sig}", on_change=save_count, args=("music_p_at_k", str(len(titles)), f"fb_p8_{sig}"))
        st.pills("Tracks that are new to you", titles, selection_mode="multi", key=f"fb_new8_{sig}",
                 on_change=save_count, args=("music_novel_k", str(len(titles)), f"fb_new8_{sig}"))
        names = [c["name"] for c in universe["creators"]]
        st.pills("Creators worth looking up", names, selection_mode="multi", key=f"fb_c6_{sig}",
                 on_change=save_count, args=("creators_p_at_k", str(len(names)), f"fb_c6_{sig}"))


def polish():
    data = state()
    universe = copy.deepcopy(data["universe"])
    universe["concept"] = creative.polish(universe["concept"], universe["vector"])
    data["universe"] = universe
    if not universe["concept"].get("polished"):
        st.session_state.flash.append("The AI wasn't available, so the template version stays.")


# ---------------------------------------------------------------
# The page
# ---------------------------------------------------------------
def create_page():
    if st.session_state.get("create_blocked"):
        st.html(safety_card_html("crisis"))
        if st.button("I'm okay, go back to Create", key="create_unblock"):
            st.session_state.create_blocked = False
            st.rerun()
        return
    if st.session_state.get("create_break"):
        break_screen(st.session_state.create_break)
    elif st.session_state.get("spark_step"):
        import spark_ui
        spark_ui.spark_screen()
    elif st.session_state.get("create_pending"):
        questions_screen()
    elif state():
        universe_screen()
    else:
        entry_screen()


def open_feel():
    go_to("Home")
