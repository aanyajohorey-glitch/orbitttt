"""
views.py
One function for each page of ORBIT:
home, mood_lab, vending_machine, universe, soundspace and collection.

app.py decides which of these functions to run, based on the page the
user picked in the navigation bar.
"""
import math
import random

import streamlit as st

from components import (
    esc, field_html, go_to, large_swatches_html, note, planet_html,
    remove_world, save_world, section_header, swatches_html, tags_html,
    world_card_html, world_dialog, world_planet,
)
from emotion_model import describe_intensity, detect_emotions, load_model
from world_data import (
    CAPSULE_COLOURS, CONSTRAINTS, INTENTS, SOUND_MOODS, SOUNDSPACES,
    load_worlds, match_world, prompt_for,
)


# ===============================================================
# 1. HOME
# ===============================================================
def hero_html():
    """The large ORBIT title with floating planets behind it."""
    stars = "".join(
        f'<span class="star" style="left:{x}%;top:{y}%;animation-delay:-{d}s"></span>'
        for x, y, d in [(12, 30, 0), (26, 72, 1.5), (38, 12, 3), (64, 82, 2), (78, 40, 4), (90, 70, 1)]
    )
    return (
        '<div class="hero">'
        '<div class="orbit-line" style="width:780px;height:250px;transform:translate(-50%,-50%) rotate(-7deg)"></div>'
        '<div class="orbit-line hide-sm" style="width:540px;height:170px;transform:translate(-50%,-50%) rotate(-7deg)"></div>'
        + stars
        + f'<div class="hero-planet hero-big" style="right:9%;top:8%">{planet_html("#E6DCF6", "#A895D2", 112, ring=True)}</div>'
        + f'<div class="hero-planet hide-sm" style="left:8%;bottom:12%">{planet_html("#F6E1E9", "#C695AA", 62, delay=3)}</div>'
        + f'<div class="hero-planet" style="left:15%;top:14%">{planet_html("#DCE5F7", "#7F93BF", 30, delay=5)}</div>'
        + f'<div class="hero-planet hide-sm" style="right:22%;bottom:8%">{planet_html("#E2EADC", "#98AA8C", 42, delay=1.5)}</div>'
        '<div class="hero-copy">'
        '<div class="eyebrow">Emotion-to-aesthetic studio</div>'
        '<div class="wordmark">ORBIT</div>'
        '<div class="tagline">Every feeling has a universe.</div>'
        "</div></div>"
    )


def home():
    worlds = load_worlds()
    st.html(hero_html())

    # --- The main question and input ---
    with st.container(key="glass-composer"):
        st.html(
            '<div class="eyebrow">Begin here</div>'
            '<div class="display" style="font-size:clamp(1.8rem,3.4vw,2.5rem)">What does your world feel like today?</div>'
            '<p class="lede">Describe a feeling, a moment or a whole day. A few honest sentences are enough.</p>'
        )
        st.text_area(
            "Your feelings",
            key="home_text",
            height=140,
            placeholder="e.g. Exams finished today. I feel relieved but strangely empty, "
                        "and I keep thinking about the long summer ahead…",
        )
        st.pills("Creative intent · optional", INTENTS, key="home_intent")

        if st.button("Find my orbit", type="primary", key="find_orbit"):
            result = analyse_mood(
                st.session_state.home_text.strip(),
                empty_message="Write a few words about how you feel first.",
            )
            if result:
                result["intent"] = st.session_state.home_intent or "Explore"
            st.session_state.home_result = result

    # --- The result, if the user pressed the button ---
    result = st.session_state.home_result
    if result:
        show_home_result(result)

    # --- Example worlds ---
    section_header(
        "Example worlds",
        "A few universes to wander through",
        "Every world in ORBIT has its own mood, palette, textures and creative prompts.",
    )
    columns = st.columns(4)
    for index, world in enumerate(worlds[:4]):
        with columns[index]:
            with st.container(key=f"glass-card-example-{index}"):
                st.html(world_card_html(world, delay=index * 1.7))
                st.button(
                    "Save world",
                    key=f"save_example_{index}",
                    on_click=save_world,
                    args=(world["name"], "Example worlds", "Explore", world["prompt_explore"]),
                    width="stretch",
                )


def other_emotions_html(emotions, limit=3, minimum=0.05):
    """Tags for the next strongest emotions, e.g. 'Nervousness · 16%'."""
    others = [(emotion, score) for emotion, score in emotions[1:] if score >= minimum][:limit]
    if not others:
        return '<span class="body">Nothing else stands out.</span>'
    return tags_html([f"{emotion.capitalize()} · {round(score * 100)}%" for emotion, score in others])


def open_in_lab(result):
    """Show the same analysis in the Mood Lab, with all the details."""
    st.session_state.lab_text = result["text"]
    st.session_state.lab_result = {key: result[key] for key in ("text", "emotions", "world", "matched")}
    go_to("Mood Lab")


def show_home_result(result):
    """The personalised result shown after pressing 'Find my orbit'."""
    world = next(w for w in load_worlds() if w["name"] == result["world"])
    prompt = prompt_for(world, result["intent"])
    primary, primary_score = result["emotions"][0]

    with st.container(key="glass-result"):
        left, right = st.columns([1, 1.8], vertical_alignment="center")
        with left:
            st.html(f'<div class="result-planet reveal">{world_planet(world, 170)}</div>')
        with right:
            st.html(
                '<div class="reveal">'
                '<span class="badge">Read by ORBIT\'s emotion model</span>'
                '<div class="stats" style="margin-top:1.1rem">'
                f'<div class="stat"><b>{esc(primary.capitalize())}</b>primary emotion · {round(primary_score * 100)}%</div>'
                f'<div class="stat"><b>{describe_intensity(primary_score, primary)}</b>intensity</div>'
                "</div>"
                + field_html("Also feeling", other_emotions_html(result["emotions"]))
                + f'<div class="eyebrow" style="margin-top:1.6rem">Your world · {esc(world["mood"])}</div>'
                f'<div class="display" style="font-size:2.4rem;margin-top:.3rem">{esc(world["name"])}</div>'
                f'<p class="body">{esc(world["description"])}</p>'
                + field_html("Matched on", tags_html(result["matched"]))
                + field_html(f'Your prompt · {esc(result["intent"])}', f'<div class="prompt">{esc(prompt)}</div>')
                + field_html("Palette", swatches_html(world["palette"]))
                + "</div>"
            )
            first, second, third = st.columns(3)
            first.button(
                "Save to collection",
                key="save_home_result",
                type="primary",
                on_click=save_world,
                args=(world["name"], "Home", result["intent"], prompt, result["text"][:160]),
                width="stretch",
            )
            second.button(
                "Full analysis",
                key="home_to_lab",
                on_click=open_in_lab,
                args=(result,),
                width="stretch",
            )
            third.button(
                "Vending machine",
                key="home_to_vending",
                on_click=go_to,
                args=("Vending Machine",),
                width="stretch",
            )
        note(
            "Detected by a pre-trained emotion model running on this device. Each emotion has its "
            "own score, so they don't add up to 100%. It understands English only and can misread "
            "sarcasm or very short texts."
        )


# ===============================================================
# 2. MOOD LAB
# ===============================================================
def mood_lab():
    section_header(
        "Mood Lab",
        "Put a feeling into words",
        "Describe how you feel. ORBIT's emotion model reads your words, finds the emotions "
        "inside them and suggests the world that matches best.",
        first=True,
    )

    left, right = st.columns([1.6, 1], gap="medium")
    with left:
        with st.container(key="glass-lab-input"):
            st.text_area(
                "Mood description",
                key="lab_text",
                height=180,
                placeholder="e.g. I'm excited about the trip but nervous about meeting new people…",
            )
            if st.button("Analyse my mood", type="primary", key="analyse"):
                st.session_state.lab_result = analyse_mood(
                    st.session_state.lab_text.strip(),
                    empty_message="Describe your mood first.",
                )
    with right:
        with st.container(key="glass-lab-steps"):
            st.html(
                '<span class="badge">Model status · connected</span>'
                '<div class="title-sm" style="margin-top:1rem">How the lab works</div>'
                '<ol class="steps">'
                "<li><span><b>Describe.</b> You write about a feeling or an experience.</span></li>"
                "<li><span><b>Detect.</b> A pre-trained model (RoBERTa, trained on GoEmotions) "
                "scores 28 emotions.</span></li>"
                "<li><span><b>Match.</b> ORBIT compares those emotions with each world in "
                "worlds.csv and picks the closest one.</span></li>"
                "</ol>"
            )

    result = st.session_state.lab_result
    if result:
        show_lab_result(result)


def analyse_mood(text, empty_message):
    """Detect emotions in the text and recommend a world.

    Used by both Home and the Mood Lab, so the model logic lives in one place.
    Returns a result dictionary, or None if the text was empty or something
    went wrong (the user sees a friendly message in that case).
    """
    if text == "":
        st.warning(empty_message)
        return None

    # The model reads words. Text with no letters at all (only numbers,
    # symbols or emoji) would give a confident but meaningless result.
    if not any(character.isalpha() for character in text):
        st.warning("ORBIT reads words. Try describing how you feel in a sentence or two.")
        return None

    # 1. Make sure the model is ready (loaded only once, then cached).
    try:
        with st.spinner("Waking up the emotion model…"):
            load_model()
    except Exception:
        st.error(
            "The emotion model couldn't be loaded. The first run needs an internet "
            "connection to download it (about 125 MB); after that it works offline."
        )
        return None

    # 2. Detect emotions and find the matching world.
    try:
        with st.spinner("Reading your words…"):
            emotions = detect_emotions(text)
            world, _, matched = match_world(emotions)
    except Exception:
        st.error("Something went wrong while reading that text. Please try again or rephrase it.")
        return None

    return {
        "text": text,
        "emotions": emotions,
        "world": world["name"],
        "matched": matched,
    }


def emotion_bars_html(emotions):
    """Horizontal bars for the strongest emotions."""
    rows = ""
    for emotion, score in emotions:
        percent = round(score * 100)
        rows += (
            f'<div class="emo-row"><span>{esc(emotion.capitalize())}</span>'
            f'<div class="emo-track"><i style="width:{max(percent, 1)}%"></i></div>'
            f'<span class="emo-pct">{percent}%</span></div>'
        )
    return rows


def show_lab_result(result):
    """The model's real result: emotions, intensity and the suggested world."""
    text = result["text"]
    emotions = result["emotions"]
    primary, primary_score = emotions[0]
    secondary = [emotion for emotion, score in emotions[1:] if score >= 0.1]
    short_text = text if len(text) <= 280 else text[:280] + "…"

    with st.container(key="glass-lab-result"):
        st.html(
            '<div class="reveal">'
            '<span class="badge">Analysed on this device · GoEmotions RoBERTa</span>'
            '<div class="field-label" style="margin-top:1.2rem">What the lab received</div>'
            f'<div class="quote">{esc(short_text)}</div>'
            '<div class="stats">'
            f'<div class="stat"><b>{esc(primary.capitalize())}</b>primary emotion</div>'
            f'<div class="stat"><b>{describe_intensity(primary_score, primary)}</b>intensity</div>'
            f'<div class="stat"><b>{esc(", ".join(secondary) if secondary else "None")}</b>also present</div>'
            "</div>"
            '<div class="field-label" style="margin-top:1.6rem">Top five emotions</div>'
            + emotion_bars_html(emotions[:5])
            + "</div>"
        )
        note(
            "Each emotion gets its own score from 0 to 100%, so the scores don't add up to 100. "
            "The model only understands English and can misread sarcasm or very short texts."
        )

    world = next(w for w in load_worlds() if w["name"] == result["world"])
    with st.container(key="glass-lab-world"):
        left, right = st.columns([1, 2.2], vertical_alignment="center")
        with left:
            st.html(f'<div class="result-planet reveal" style="min-height:190px">{world_planet(world, 130)}</div>')
        with right:
            st.html(
                '<div class="reveal">'
                '<div class="eyebrow">Suggested world</div>'
                f'<div class="display" style="font-size:2.2rem;margin-top:.3rem">{esc(world["name"])}</div>'
                f'<p class="body">{esc(world["mood"])}. {esc(world["description"])}</p>'
                + field_html("Matched on", tags_html(result["matched"]))
                + field_html("Prompt · Explore", f'<div class="prompt">{esc(world["prompt_explore"])}</div>')
                + "</div>"
            )
            st.button(
                "Save to collection",
                key="save_lab_world",
                type="primary",
                on_click=save_world,
                args=(world["name"], "Mood Lab", "Explore", world["prompt_explore"], text[:160]),
            )


# ===============================================================
# 3. AESTHETIC VENDING MACHINE
# ===============================================================
def make_pack(previous=None):
    """Pick a random world, intent and constraint for a creative pack."""
    worlds = load_worlds()
    world = random.choice(worlds)
    # On reroll, try not to give the same world twice in a row.
    while previous and world["name"] == previous["world"] and len(worlds) > 1:
        world = random.choice(worlds)
    return {
        "world": world["name"],
        "intent": random.choice(INTENTS),
        "constraint": random.choice(CONSTRAINTS),
    }


def choose_capsule(number):
    st.session_state.capsule = number
    st.session_state.pack = make_pack()


def reroll_pack():
    st.session_state.pack = make_pack(st.session_state.pack)


def return_capsule():
    st.session_state.capsule = None
    st.session_state.pack = None


def vending_machine():
    section_header(
        "Aesthetic Vending Machine",
        "Pick a capsule. Get a creative pack.",
        "Each mystery capsule holds a world, a prompt and one small creative challenge. "
        "Packs are chosen at random, so reroll as often as you like.",
        first=True,
    )

    chosen = st.session_state.capsule
    with st.container(key="glass-machine"):
        st.html('<div class="eyebrow">Choose a capsule</div><div class="machine-window"></div>')
        columns = st.columns(len(CAPSULE_COLOURS))
        for number, colour in enumerate(CAPSULE_COLOURS):
            if chosen is None:
                state = ""
            elif chosen == number:
                state = "selected"
            else:
                state = "dim"
            with columns[number]:
                st.html(
                    '<div class="capsule-slot">'
                    f'<div class="capsule {state}" style="--c:{colour};animation-delay:-{number * 1.3}s"></div>'
                    f'<div class="capsule-num">{number + 1:02d}</div></div>'
                )
                st.button(
                    "Chosen" if chosen == number else "Choose",
                    key=f"capsule_{number}",
                    on_click=choose_capsule,
                    args=(number,),
                    width="stretch",
                )

    pack = st.session_state.pack
    if pack:
        show_pack(pack, chosen)
    else:
        note("Choose any capsule to reveal a sample creative pack.")


def show_pack(pack, capsule_number):
    world = next(w for w in load_worlds() if w["name"] == pack["world"])
    prompt = prompt_for(world, pack["intent"])

    with st.container(key="glass-pack"):
        left, right = st.columns([1, 1.9], vertical_alignment="center")
        with left:
            st.html(f'<div class="result-planet reveal">{world_planet(world, 150)}</div>')
        with right:
            st.html(
                '<div class="reveal">'
                f'<div class="eyebrow">Capsule {capsule_number + 1:02d} · Creative pack</div>'
                f'<div class="display" style="font-size:2.3rem;margin-top:.35rem">{esc(world["name"])}</div>'
                f'<p class="body">{esc(world["mood"])}. {esc(world["description"])}</p>'
                + field_html(f'Prompt · {esc(pack["intent"])}', f'<div class="prompt">{esc(prompt)}</div>')
                + field_html("Constraint", esc(pack["constraint"]))
                + "</div>"
            )
        st.html(
            '<div class="meta-grid reveal">'
            + field_html("Palette", large_swatches_html(world["palette"]))
            + field_html("Visual elements", tags_html(world["elements"]))
            + field_html("Typography", esc(world["typography"]))
            + field_html("Sound vibe", esc(world["sound"]))
            + "</div>"
        )
        first, second, third = st.columns(3)
        first.button("Reroll", key="reroll", on_click=reroll_pack, width="stretch")
        second.button(
            "Save to collection",
            key="save_pack",
            type="primary",
            on_click=save_world,
            args=(world["name"], "Vending Machine", pack["intent"], prompt, "", pack["constraint"]),
            width="stretch",
        )
        third.button("Return capsule", key="return_capsule", on_click=return_capsule, width="stretch")


# ===============================================================
# 4. ORBIT UNIVERSE
# ===============================================================
def orbit_map_html(items):
    """Saved planets arranged around an oval orbit."""
    stops = ""
    for index, item in enumerate(items):
        world = next(w for w in load_worlds() if w["name"] == item["world"])
        angle = 2 * math.pi * index / len(items) - math.pi / 2
        x = 50 + 40 * math.cos(angle)
        y = 50 + 34 * math.sin(angle)
        stops += (
            f'<div class="orbit-stop" style="left:{x:.1f}%;top:{y:.1f}%">'
            f'{world_planet(world, 46, index * 1.1)}<small>{esc(world["name"])}</small></div>'
        )
    label = "world" if len(items) == 1 else "worlds"
    return (
        '<div class="orbit-map"><div class="orbit-path"></div>'
        f'<div class="orbit-core"><b>{len(items)}</b><span>saved {label}</span></div>'
        f"{stops}</div>"
    )


def empty_state(title, text):
    st.html(
        '<div class="empty">'
        + planet_html("#EFEAF7", "#C9B9E8", 70, ring=True)
        + f'<div class="title-sm">{title}</div><p class="body">{text}</p></div>'
    )
    _, left, right, _ = st.columns([1, 1.2, 1.2, 1])
    left.button("Find my orbit", key=f"empty_home_{title}", type="primary", on_click=go_to, args=("Home",), width="stretch")
    right.button("Open a capsule", key=f"empty_vend_{title}", on_click=go_to, args=("Vending Machine",), width="stretch")


def universe():
    section_header(
        "ORBIT Universe",
        "Your saved worlds",
        "Every world you save becomes a planet in your universe. Open one to see its palette, "
        "prompt and details.",
        first=True,
    )
    items = st.session_state.collection
    if not items:
        empty_state("Your universe is still quiet", "Save a world from Home or the Vending Machine and it will appear here.")
        return

    st.html(orbit_map_html(items))

    columns = st.columns(3)
    for index, item in enumerate(items):
        world = next(w for w in load_worlds() if w["name"] == item["world"])
        with columns[index % 3]:
            with st.container(key=f"glass-card-saved-{item['id']}"):
                st.html(world_card_html(world, index * 1.3, subtitle=f'{item["intent"]} · {item["source"]}'))
                if st.button("Open world", key=f"open_universe_{item['id']}", width="stretch"):
                    world_dialog(item)


# ===============================================================
# 5. SOUNDSPACE
# ===============================================================
def wave_html(colour):
    """A small decorative sound wave (it does not play anything)."""
    heights = [10, 18, 26, 14, 22, 30, 16, 24, 12, 20, 28, 14]
    bars = "".join(
        f'<span style="height:{h}px;animation-delay:-{i * 0.21:.2f}s"></span>' for i, h in enumerate(heights)
    )
    return f'<div class="wave" style="--c:{colour}">{bars}</div>'


def soundspace():
    section_header(
        "Soundspace",
        "Music for the world you're in",
        "Listening vibes that match each world: genres, tempo and the kind of creative work they suit.",
        first=True,
    )
    note(
        "Soundspace suggests vibes only. It doesn't play music and isn't connected to Spotify "
        "or any other streaming service yet."
    )
    st.html('<div style="height:.6rem"></div>')
    mood = st.pills("Filter by mood", SOUND_MOODS, key="sound_mood")

    vibes = [v for v in SOUNDSPACES if mood is None or mood in v["moods"]]
    columns = st.columns(3)
    for index, vibe in enumerate(vibes):
        with columns[index % 3]:
            with st.container(key=f"glass-card-sound-{index}"):
                st.html(
                    wave_html(vibe["colour"])
                    + f'<div class="eyebrow">{esc(vibe["genres"])}</div>'
                    + f'<div class="title-sm">{esc(vibe["name"])}</div>'
                    + tags_html(vibe["moods"])
                    + '<div class="meta-grid">'
                    + field_html("Tempo", esc(vibe["tempo"]))
                    + field_html("Pairs with", esc(vibe["pairs_with"]))
                    + "</div>"
                    + field_html("Best for", esc(vibe["best_for"]))
                )


# ===============================================================
# 6. MY COLLECTION
# ===============================================================
def collection():
    section_header(
        "My Collection",
        "Worlds you've kept",
        "Everything you save from Home, the example worlds or the Vending Machine is kept here.",
        first=True,
    )
    note(
        "Your collection is stored with Streamlit's session state, so it lasts only while this "
        "session is open. Refreshing the page, closing the tab or restarting the app will reset it."
    )
    items = st.session_state.collection
    if not items:
        empty_state("Nothing saved yet", "Worlds you save will be listed here.")
        return

    st.html('<div style="height:.8rem"></div>')
    for item in reversed(items):  # newest first
        world = next(w for w in load_worlds() if w["name"] == item["world"])
        with st.container(key=f"glass-item-{item['id']}"):
            planet_col, info_col, action_col = st.columns([0.8, 4, 1.3], vertical_alignment="center")
            with planet_col:
                st.html(f'<div style="display:flex;justify-content:center">{world_planet(world, 64)}</div>')
            with info_col:
                st.html(
                    f'<div class="eyebrow">{esc(item["source"])} · {esc(item["intent"])} · {esc(item["saved_at"])}</div>'
                    f'<div class="title-sm">{esc(world["name"])}</div>'
                    f'<p class="body">{esc(item["prompt"])}</p>'
                    + swatches_html(world["palette"])
                )
            with action_col:
                if st.button("Open", key=f"open_item_{item['id']}", width="stretch"):
                    world_dialog(item)
                st.button(
                    "Remove",
                    key=f"remove_{item['id']}",
                    type="tertiary",
                    on_click=remove_world,
                    args=(item["id"],),
                    width="stretch",
                )
