"""
views.py
Shared pieces for the check-in, and the Saved worlds, Soundspace and
Collection pages. The other pages have their own files:

    today.py      Check-in              vending.py    Vending Machine (arcade)
    wrapped.py    Wrapped (My Galaxy)   patterns.py   Patterns

app.py decides which page function to run.
"""
import math
from datetime import datetime

import streamlit as st

import storage
from companion import reply
from components import (
    esc, field_html, go_to, note, planet_html, remove_world, save_world, section_header, swatches_html,
    tags_html, world_card_html, world_dialog, world_planet,
)
from emotion_model import describe_intensity
from theme import set_world
from world_data import SOUND_MOODS, SOUNDSPACES, load_worlds


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


def other_emotions_html(emotions, primary=None, limit=3, minimum=0.05):
    """Tags for the next strongest emotions, e.g. 'Nervousness · 16%'."""
    others = [(e, s) for e, s in emotions if e != primary and s >= minimum][:limit]
    if not others:
        return '<span class="body">Nothing else stands out.</span>'
    return tags_html([f"{emotion.capitalize()} · {round(score * 100)}%" for emotion, score in others])


def refresh_home(result):
    """After the user teaches ORBIT, rewrite the companion's reply."""
    result["reply"], result["style"] = reply(result, name=storage.get_setting("name", ""))
    set_world(result)


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
        empty_state("Your universe is still quiet", "Save a world from Today or the Arcade and it will appear here.")
    else:
        st.html(orbit_map_html(items))
        saved_cards(items)
    discover_worlds()


def discover_worlds():
    """Example worlds anyone can explore and save (moved here from the old Home page)."""
    worlds = load_worlds()
    section_header("Discover worlds", "A few universes to wander through",
                   "Every world in ORBIT has its own mood, palette, textures and creative prompts.")
    columns = st.columns(4)
    for index, world in enumerate(worlds[:4]):
        with columns[index]:
            with st.container(key=f"glass-card-example-{index}"):
                st.html(world_card_html(world, delay=index * 1.7))
                st.button("Save world", key=f"save_example_{index}", on_click=save_world,
                          args=(world["name"], "Example worlds", "Explore", world["prompt_explore"]), width="stretch")


def saved_cards(items):
    columns = st.columns(3)
    for index, item in enumerate(items):
        world = next(w for w in load_worlds() if w["name"] == item["world"])
        with columns[index % 3]:
            with st.container(key=f"glass-card-saved-{item['id']}"):
                st.html(world_card_html(world, index * 1.3, subtitle=f'{item["intent"]} · {item["source"]}'))
                if st.button("Open world", key=f"open_universe_{item['id']}", width="stretch"):
                    world_dialog(item)


VIBE_SONGS = {
    "Dream Pop Haze": (3.6, 2.4, ["dreamy", "calm", "night"]),
    "Neo-classical Rain": (2.8, 1.6, ["calm", "instrumental", "rain", "classical"]),
    "Indie Folk Morning": (4.0, 2.6, ["acoustic", "folk", "morning", "hopeful"]),
    "City Pop Sunset": (4.0, 3.4, ["nostalgic", "summer", "dance"]),
    "Late-night Jazz": (3.0, 2.0, ["night", "chill", "calm"]),
    "Cinematic Electronica": (3.2, 3.4, ["instrumental", "journey", "focus"]),
    "Soft Ambient": (3.0, 1.3, ["calm", "instrumental", "focus"]),
}


def vibe_songs(name, size=4):
    """Real songs for a Soundspace vibe, from ORBIT's own 271-song catalogue (music.py)."""
    import music
    mood, energy, tags = VIBE_SONGS[name]
    return music.recommend_target(mood, energy, tags, intent="match", discovery=0.3, size=size)


def songs_html(tracks):
    import music
    rows = []
    for track in tracks:
        spotify, youtube = music.links(track)
        rows.append(f'<div class="track"><div><b>{esc(track["title"])}</b> · {esc(track["artist"])}'
                    f'<small>{esc(track["language"])} · {esc(track["genre"])}</small></div>'
                    f'<div class="track-links"><a href="{spotify}" target="_blank" rel="noopener">Spotify</a>'
                    f'<a href="{youtube}" target="_blank" rel="noopener">YouTube</a></div></div>')
    return '<div class="sound-songs">' + "".join(rows) + "</div>"


def wave_html(colour):
    """A small decorative sound wave."""
    heights = [10, 18, 26, 14, 22, 30, 16, 24, 12, 20, 28, 14]
    bars = "".join(
        f'<span style="height:{h}px;animation-delay:-{i * 0.21:.2f}s"></span>' for i, h in enumerate(heights)
    )
    return f'<div class="wave" style="--c:{colour}">{bars}</div>'


def soundspace():
    section_header(
        "Soundspace",
        "Music for the world you're in",
        "Listening vibes that match each world, each with real songs to play in Spotify or YouTube.",
        first=True,
    )
    note("Songs come from ORBIT's own hand-picked catalogue. The links open a search in Spotify or YouTube: "
         "ORBIT doesn't stream music itself.")

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
                    + field_html("Songs", songs_html(vibe_songs(vibe["name"])))
                )


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
    for item in reversed(items):
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
