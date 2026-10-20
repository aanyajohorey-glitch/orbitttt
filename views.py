"""
views.py
The main pages of ORBIT: Home, Mood Lab, ORBIT Universe, Soundspace and
My Collection. The other pages have their own files:

    companion.py  Companion chat        calm_room.py  Calm Room
    journal.py    Journal               vending.py    Vending Machine (arcade)
    ai_lab.py     AI Lab                care.py       Care (safety & privacy)

app.py decides which page function to run.
"""
import hashlib
import math
from datetime import datetime

import streamlit as st

import storage
import voice
from analysis import analyse, record_checkin
from companion import companion_card_html, open_calm_room, reply, suggestion
from components import (
    esc, field_html, go_to, note, planet_html, remove_world, save_world, section_header, swatches_html,
    tags_html, world_card_html, world_dialog, world_planet,
)
from emotion_model import describe_intensity
from explain import highlight_html, top_words, word_importance
from safety import safety_card_html
from soundscapes import soundscape
from teach_ui import clarify, confidence_html, teach_panel
from world_data import INTENTS, SOUND_MOODS, SOUNDSPACES, load_worlds, prompt_for


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
        '<div class="eyebrow">Your emotional wellbeing companion</div>'
        '<div class="wordmark">ORBIT</div>'
        '<div class="tagline">Every feeling has a universe.</div>'
        "</div></div>"
    )


def greeting(name):
    hour = datetime.now().hour
    part = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening"
    return f"Good {part}{', ' + esc(name) if name else ''}"


def save_home_name():
    storage.set_setting("name", st.session_state.home_name.strip())


def keep_talking(result):
    """Continue the conversation from Home in the Companion chat."""
    st.session_state.chat = [
        {"role": "user", "content": result["text"], "result": result},
        {"role": "assistant", "content": result["reply"], "style": result["style"], "result": result},
    ]
    st.session_state.chat_token_given = True
    go_to("Companion")


def home():
    worlds = load_worlds()
    name = storage.get_setting("name", "")
    st.html(hero_html())

    # --- The check-in ---
    with st.container(key="glass-composer"):
        st.html(
            f'<div class="eyebrow">{greeting(name)} · Begin here</div>'
            '<div class="display" style="font-size:clamp(1.8rem,3.4vw,2.5rem)">What does your world feel like today?</div>'
            '<p class="lede">Describe a feeling, a moment or a whole day, in English or Hinglish. '
            "A few honest sentences are enough.</p>"
        )
        if not name:
            st.text_input("What should ORBIT call you? (optional)", key="home_name", on_change=save_home_name,
                          max_chars=30, placeholder="Your first name or a nickname")
        st.text_area(
            "Your feelings",
            key="home_text",
            height=140,
            placeholder="e.g. Exams finished today. I feel relieved but strangely empty, "
                        "and I keep thinking about the long summer ahead…",
        )
        st.pills("Creative intent · optional", INTENTS, key="home_intent")

        if st.button("Find my orbit", type="primary", key="find_orbit"):
            result = analyse(
                st.session_state.home_text.strip(),
                empty_message="Write a few words about how you feel first.",
            )
            if result:
                result["intent"] = st.session_state.home_intent or "Explore"
                result["reply"], result["style"] = reply(result, name=name)
                record_checkin(result, "Home")
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


def other_emotions_html(emotions, primary=None, limit=3, minimum=0.05):
    """Tags for the next strongest emotions, e.g. 'Nervousness · 16%'."""
    others = [(e, s) for e, s in emotions if e != primary and s >= minimum][:limit]
    if not others:
        return '<span class="body">Nothing else stands out.</span>'
    return tags_html([f"{emotion.capitalize()} · {round(score * 100)}%" for emotion, score in others])


def open_in_lab(result):
    """Show the same analysis in the Mood Lab, with all the details."""
    st.session_state.lab_text = result["text"]
    st.session_state.lab_result = {key: result[key] for key in
                                   ("text", "model_text", "translated", "emotions", "raw_scores", "final",
                                    "world", "matched", "safety")}
    st.session_state.lab_explain = None
    go_to("Mood Lab")


def refresh_home(result):
    """After the user teaches ORBIT, rewrite the companion's reply."""
    result["reply"], result["style"] = reply(result, name=storage.get_setting("name", ""))


def final_stats_html(result):
    """ORBIT's final reading: emotion, family, confidence and intensity."""
    final = result["final"]
    score = dict(result["emotions"]).get(final["emotion"], 0.0)
    label = "best guess" if final["unsure"] else "main feeling"
    if final["source"] == "your correction":
        confidence = '<div class="stat"><b>You</b>told ORBIT this feeling</div>'
    elif final.get("vague"):
        confidence = '<div class="stat"><b>Asking</b>message too short or vague to be sure</div>'
    else:
        confidence = f'<div class="stat"><b>{final["confidence"]:.0%}</b>confidence</div>'
    return (
        '<div class="stats" style="margin-top:1.1rem">'
        f'<div class="stat"><b>{esc(final["emotion"].capitalize())}</b>{label} · {esc(final["family"])}</div>'
        + confidence
        + f'<div class="stat"><b>{describe_intensity(score, final["emotion"])}</b>intensity (base model)</div>'
        "</div>"
    )


def understood_html(result):
    if not result["translated"]:
        return ""
    return (f'<p class="understood">ORBIT translated your Hinglish/Hindi and understood it as: '
            f'<i>“{esc(result["model_text"])}”</i></p>')


def show_home_result(result):
    """The personalised result shown after pressing 'Find my orbit'."""
    world = next(w for w in load_worlds() if w["name"] == result["world"])
    prompt = prompt_for(world, result["intent"])
    primary = result["final"]["emotion"]

    if result["safety"]:
        st.html(safety_card_html(result["safety"]))

    # The companion's reply comes first: being heard matters most.
    tool, line = suggestion(result)
    with st.container(key="glass-companion"):
        st.html(companion_card_html(result["reply"], result["style"]))
        asked = clarify(result, key="home_clarify", on_update=refresh_home)
        if result["safety"] != "crisis" and not asked:
            st.html(f'<p class="body" style="margin:.4rem 0 .2rem">{esc(line)}</p>')
        first, second, third = st.columns(3)
        first.button("Keep talking", key="home_talk", type="primary", on_click=keep_talking, args=(result,),
                     width="stretch")
        if result["safety"] != "crisis":
            second.button(f"Try {tool}", key="home_tool", on_click=open_calm_room, args=(tool,), width="stretch")
        third.button("Full analysis", key="home_to_lab", on_click=open_in_lab, args=(result,), width="stretch")

    if result["safety"] == "crisis":
        return  # no creative suggestions when someone may be in danger

    with st.container(key="glass-result"):
        left, right = st.columns([1, 1.8], vertical_alignment="center")
        with left:
            st.html(f'<div class="result-planet reveal">{world_planet(world, 170)}</div>')
        with right:
            st.html(
                '<div class="reveal">'
                f'<span class="badge">Read by {esc(result["final"]["source"])}</span> '
                + confidence_html(result)
                + understood_html(result)
                + final_stats_html(result)
                + field_html("Also feeling", other_emotions_html(result["emotions"], primary))
                + f'<div class="eyebrow" style="margin-top:1.6rem">'
                f'{"A first guess at your world · answer above to refine it" if result["final"]["unsure"] else "Your world"}'
                f' · {esc(world["mood"])}</div>'
                f'<div class="display" style="font-size:2.4rem;margin-top:.3rem">{esc(world["name"])}</div>'
                f'<p class="body">{esc(world["description"])}</p>'
                + field_html("Matched on", tags_html(result["matched"]))
                + field_html(f'Your prompt · {esc(result["intent"])}', f'<div class="prompt">{esc(prompt)}</div>')
                + field_html("Palette", swatches_html(world["palette"]))
                + "</div>"
            )
            first, second = st.columns(2)
            first.button(
                "Save to collection",
                key="save_home_result",
                type="primary",
                on_click=save_world,
                args=(world["name"], "Home", result["intent"], prompt, result["text"][:160]),
                width="stretch",
            )
            second.button(
                "Vending machine",
                key="home_to_vending",
                on_click=go_to,
                args=("Vending Machine",),
                width="stretch",
            )
        teach_panel(result, key="home_teach", on_update=refresh_home)
        note(
            "A pre-trained emotion model scores 28 feelings, then ORBIT's own trained classifier picks the "
            "main feeling and says how sure it is. Everything runs on this device. It can still misread "
            "sarcasm or very short texts: if it's wrong, you can teach it."
        )


# ===============================================================
# 2. MOOD LAB
# ===============================================================
def mood_lab():
    section_header(
        "Mood Lab",
        "Put a feeling into words",
        "A deeper look at your emotions: all the strongest feelings, the words that caused them, and the "
        "world that matches best. Type, paste Hinglish, or record a voice note.",
        first=True,
    )

    left, right = st.columns([1.6, 1], gap="medium")
    with left:
        with st.container(key="glass-lab-input"):
            voice_input()
            st.text_area(
                "Mood description",
                key="lab_text",
                height=180,
                placeholder="e.g. I'm excited about the trip but nervous about meeting new people…",
            )
            if st.button("Analyse my mood", type="primary", key="analyse"):
                result = analyse(st.session_state.lab_text.strip(), empty_message="Describe your mood first.")
                st.session_state.lab_result = result
                st.session_state.lab_explain = None
                if result:
                    record_checkin(result, "Mood Lab")
    with right:
        with st.container(key="glass-lab-steps"):
            st.html(
                '<span class="badge">Model status · connected</span>'
                '<div class="title-sm" style="margin-top:1rem">How the lab works</div>'
                '<ol class="steps">'
                "<li><span><b>Describe.</b> You write (or say) how you feel.</span></li>"
                "<li><span><b>Translate.</b> Hinglish and Hindi words are turned into English.</span></li>"
                "<li><span><b>Detect.</b> A pre-trained model (RoBERTa, trained on GoEmotions) "
                "scores 28 emotions.</span></li>"
                "<li><span><b>Explain.</b> ORBIT shows which of your words mattered most.</span></li>"
                "<li><span><b>Match.</b> The closest world from worlds.csv is suggested.</span></li>"
                "</ol>"
            )

    result = st.session_state.lab_result
    if result:
        show_lab_result(result)


def voice_input():
    audio = st.audio_input("Or record a voice note", key="lab_voice")
    if audio is None:
        return
    data = audio.getvalue()
    digest = hashlib.md5(data).hexdigest()
    if st.session_state.get("lab_voice_done") == digest:
        return
    if not voice.available():
        note("Voice notes need a free speech-recognition model (faster-whisper). Ask to have it installed; "
             "until then, please type instead.")
        return
    with st.spinner("Listening to your voice note…"):
        text = voice.transcribe(data)
    st.session_state.lab_voice_done = digest
    if text:
        st.session_state.lab_text = text  # fills the text box below
    else:
        st.warning("I couldn't hear any words in that recording. Please try again.")


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


def run_explanation():
    result = st.session_state.lab_result
    emotion = result["final"]["emotion"]
    st.session_state.lab_explain = (emotion, word_importance(result["model_text"], emotion))


def show_lab_result(result):
    """The model's real result: emotions, intensity and the suggested world."""
    text = result["text"]
    emotions = result["emotions"]
    primary = result["final"]["emotion"]
    secondary = [e for e, score in emotions if e != primary and score >= 0.1]
    short_text = text if len(text) <= 280 else text[:280] + "…"

    if result.get("safety"):
        st.html(safety_card_html(result["safety"]))

    with st.container(key="glass-lab-result"):
        st.html(
            '<div class="reveal">'
            f'<span class="badge">Analysed on this device · {esc(result["final"]["source"])}</span> '
            + confidence_html(result)
            + '<div class="field-label" style="margin-top:1.2rem">What the lab received</div>'
            f'<div class="quote">{esc(short_text)}</div>'
            + understood_html(result)
            + final_stats_html(result)
            + field_html("Also present", esc(", ".join(secondary) if secondary else "Nothing else stands out"))
            + '<div class="field-label" style="margin-top:1.6rem">The base model\'s five strongest scores</div>'
            + emotion_bars_html(emotions[:5])
            + "</div>"
        )
        if result.get("safety") != "crisis":
            clarify(result, key="lab_clarify")
            teach_panel(result, key="lab_teach")
        note(
            "The bars are the pre-trained RoBERTa model's own scores (each from 0 to 100%, so they don't add "
            "up to 100). ORBIT's trained classifier then decides the main feeling, which can differ: for "
            "example, a racing heart before a presentation scores high on excitement, but usually means nerves."
        )

    if result.get("safety") == "crisis":
        return  # only help is shown when someone may be in danger

    with st.container(key="glass-lab-why"):
        st.html('<div class="eyebrow">Explainable AI</div>'
                f'<div class="title-sm">Why does ORBIT think this is {esc(primary)}?</div>')
        explained = st.session_state.get("lab_explain")
        if explained and explained[0] == primary:
            words = top_words(explained[1])
            st.html(highlight_html(explained[1])
                    + '<p class="body">'
                    + (f"The words that pushed the model most towards <b>{esc(primary)}</b>: "
                       + ", ".join(f"<b>“{esc(w)}”</b>" for w in words) + "." if words
                       else "No single word stood out: the feeling comes from the sentence as a whole.")
                    + " ORBIT found this by removing one word at a time and measuring how much the score "
                    "dropped.</p>")
        else:
            st.html('<p class="body">See which of your words made the AI decide. It takes a few seconds.</p>')
            st.button("Explain this result", key="lab_why", on_click=run_explanation)

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
# 3. ORBIT UNIVERSE
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
# 4. SOUNDSPACE
# ===============================================================
# Which generated soundscape (soundscapes.py) plays for each vibe
SOUND_KIND = {
    "Dream Pop Haze": ("dream", "a soft, dreamy chord"),
    "Neo-classical Rain": ("rain", "gentle rain"),
    "Indie Folk Morning": ("sunset", "a warm morning chord"),
    "City Pop Sunset": ("sunset", "a golden-hour chord"),
    "Late-night Jazz": ("night", "night crickets and a low chord"),
    "Cinematic Electronica": ("focus", "a slow focus drone"),
    "Soft Ambient": ("waves", "slow ocean waves"),
}


def wave_html(colour):
    """A small decorative sound wave."""
    heights = [10, 18, 26, 14, 22, 30, 16, 24, 12, 20, 28, 14]
    bars = "".join(
        f'<span style="height:{h}px;animation-delay:-{i * 0.21:.2f}s"></span>' for i, h in enumerate(heights)
    )
    return f'<div class="wave" style="--c:{colour}">{bars}</div>'


def play_vibe(name):
    st.session_state.now_playing = name


def stop_vibe():
    st.session_state.now_playing = None


def soundspace():
    section_header(
        "Soundspace",
        "Music for the world you're in",
        "Listening vibes that match each world. Press play to hear a calming soundscape that ORBIT "
        "creates itself.",
        first=True,
    )
    note(
        "Soundscapes are generated by ORBIT with Python maths (sine waves and filtered noise), so they work "
        "offline. Genre suggestions are just ideas: ORBIT isn't connected to Spotify or any streaming service."
    )

    playing = st.session_state.get("now_playing")
    if playing:
        kind, description = SOUND_KIND[playing]
        with st.container(key="glass-player"):
            st.html(f'<div class="eyebrow">Now playing · {esc(playing)}</div>'
                    f'<p class="body" style="margin:.2rem 0 .6rem">A loop of {esc(description)}. '
                    "Close your eyes and breathe slowly.</p>")
            st.audio(soundscape(kind), format="audio/wav", loop=True, autoplay=True)
            st.button("Stop", key="sound_stop", on_click=stop_vibe)

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
                is_playing = playing == vibe["name"]
                st.button("Playing" if is_playing else "Play soundscape", key=f"play_{index}",
                          type="primary" if is_playing else "secondary", on_click=play_vibe,
                          args=(vibe["name"],), width="stretch")


# ===============================================================
# 5. MY COLLECTION
# ===============================================================
def collection():
    section_header(
        "My Collection",
        "Worlds you've kept",
        "Everything you save from Home, the Mood Lab, the example worlds or the Vending Machine is kept here.",
        first=True,
    )
    note(
        "Saved worlds are stored privately on this computer (data/orbit.db), so they stay after you refresh "
        "the page or restart the app. You can delete them here or all at once on the Care page."
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
