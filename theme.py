"""
theme.py
The whole app changes world with you.

When ORBIT detects a feeling, the app takes on that feeling's world from
data/worlds.csv: the background gradient (from the world's palette), the
accent colour, the glow around cards, and how fast things float ("motion").

How the smooth change works: CSS can't fade one gradient into another, so
the OLD world's gradient is drawn on a layer in front of the background and
faded out, revealing the new world underneath.

The theme is NOT applied when:
- the message was a crisis (the app stays calm and neutral; help comes first)
- "High contrast" is on (readability matters more than mood colours)
Reduce motion switches the fade and floating off (see styles.REDUCED_MOTION_CSS).

Background music: a calm general soundscape plays until ORBIT knows your mood,
then the soundscape of your world. It can be switched off in Settings. The
"Start Exploring Your Universe" tap counts as the first tap browsers need
before they allow sound.
"""
import hashlib

import streamlit as st

from soundscapes import soundscape
from world_data import SOUNDSPACES, get_world

SPEED = {"slow": 1.5, "medium": 1.0, "lively": 0.65}
SOUND_FOR_SPACE = {"Dream Pop Haze": "dream", "Neo-classical Rain": "rain", "Indie Folk Morning": "sunset",
                   "City Pop Sunset": "sunset", "Late-night Jazz": "focus", "Cinematic Electronica": "waves",
                   "Soft Ambient": "night"}


def set_world(result):
    """Called after every analysis. Crisis -> back to ORBIT's neutral look."""
    new = None if not result or result.get("safety") == "crisis" else result.get("world")
    if new != st.session_state.get("world_theme"):
        st.session_state.world_from = st.session_state.get("world_theme")
        st.session_state.world_theme = new


def reset_world():
    st.session_state.world_from = st.session_state.get("world_theme")
    st.session_state.world_theme = None


def lookup(name):
    """A world from worlds.csv, or a Creator Mode "vibe world" made from a universe's palette."""
    if not name:
        return None
    if name.startswith("vibe:"):
        return st.session_state.get("vibe_worlds", {}).get(name)
    return get_world(name)


def active_world():
    return lookup(st.session_state.get("world_theme"))


def set_vibe_world(universe):
    """Creator Mode: the app takes on the current universe's palette and energy."""
    colours = {c["role"]: c["hex"] for c in universe["palette"]["colours"]}
    arousal = universe["vector"]["arousal"]
    name = "vibe:" + universe["concept"]["title"]
    world = {"name": universe["concept"]["title"], "mood": "your creative universe",
             "palette": [colours["Primary"], colours["Harmony A"], colours["Harmony B"]],
             "planet_light": colours["Harmony A"], "planet_dark": colours["Primary"], "ring": False,
             "motion": "lively" if arousal > 0.35 else "slow" if arousal < -0.2 else "medium",
             "sound": "sunset" if arousal > 0.35 else "rain" if arousal < -0.2 else "dream"}
    st.session_state.setdefault("vibe_worlds", {})[name] = world
    if name != st.session_state.get("world_theme"):
        st.session_state.world_from = st.session_state.get("world_theme")
        st.session_state.world_theme = name


def _rgba(hex_colour, alpha):
    hex_colour = hex_colour.lstrip("#")
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"


def gradient(world, night=False):
    """The page background for a world (soft, so text stays easy to read). Night mode: a dark base."""
    if world is None:
        a, b, c = "#C9B9E8", "#B9C8EA", "#EBCBD7"
    else:
        a, b, c = world["palette"][:3]
    base = "#15131D" if night else "#F8F6F2"
    return (f"radial-gradient(1100px 560px at 88% -8%, {_rgba(a, 0.42)}, transparent 60%), "
            f"radial-gradient(900px 520px at -12% 24%, {_rgba(b, 0.34)}, transparent 60%), "
            f"radial-gradient(900px 600px at 50% 112%, {_rgba(c, 0.32)}, transparent 60%), {base}")


def theme_css(settings):
    """CSS for the active world. settings: the accessibility settings."""
    if settings.get("high_contrast"):
        return ""
    world = active_world()
    old_name = st.session_state.get("world_from")
    old = lookup(old_name)
    css = []
    if world is not None:
        accent = world["planet_dark"]
        light = world["planet_light"]
        speed = SPEED.get(world.get("motion", "medium"), 1.0)
        css.append(f"""
:root {{ --lavender: {world["palette"][0]}; --accent: {accent}; --orbit-speed: {speed}; }}
.stApp {{ background: {gradient(world, settings.get('night_mode'))}; background-attachment: fixed; }}
[class*="st-key-glass"] {{ box-shadow: 0 24px 50px -30px {_rgba(accent, 0.55)}, 0 0 0 1px {_rgba(accent, 0.12)},
  0 0 42px -18px {_rgba(accent, 0.45)} !important; }}
[data-testid="stBaseButton-primary"] {{ background: linear-gradient(180deg, {light} 0%, {_rgba(accent, 0.75)} 100%) !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.65), 0 12px 26px -14px {_rgba(accent, 0.8)} !important; }}
.st-key-nav [data-testid="stBaseButton-primary"] {{ background: {_rgba(accent, 0.32)} !important; }}
.planet, .hero-planet .planet {{ animation-duration: calc(9s * var(--orbit-speed)) !important; }}
.why-word {{ background: {_rgba(accent, 0.25)}; box-shadow: 0 0 calc(var(--w) * 14px) {_rgba(accent, 0.55)}; }}
""")
    if old_name != st.session_state.get("world_theme"):
        name = "worldfade" + hashlib.md5(f"{old_name}>{st.session_state.get('world_theme')}".encode()).hexdigest()[:6]
        css.append(f"""
.stApp::before {{ content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background: {gradient(old, settings.get('night_mode'))}; animation: {name} 1.8s ease forwards; }}
@keyframes {name} {{ from {{ opacity: 1; }} to {{ opacity: 0; }} }}
[data-testid="stAppViewContainer"] {{ position: relative; z-index: 1; }}
""")
    return "\n".join(css)


@st.cache_data(show_spinner=False)
def world_sound(kind):
    """The soundscape is made once and then remembered (it takes a moment to build)."""
    return soundscape(kind)


def sound_kind(world):
    if world.get("sound"):
        return world["sound"]
    for space in SOUNDSPACES:
        if space["pairs_with"] == world["name"]:
            return SOUND_FOR_SPACE[space["name"]]
    return "sunset"


def world_bar():
    """The world you're in and a way back. Shown only after a feeling has been detected."""
    world = active_world()
    if world is None:
        return
    left, middle = st.columns([3, 1.2], vertical_alignment="center")
    left.html(f'<div class="world-chip"><span style="--c:{world["planet_dark"]}"></span>'
              f'You are in <b>{world["name"]}</b> · {world["mood"]}</div>')
    middle.button("Back to ORBIT's colours", key="world_reset", type="tertiary", on_click=reset_world)


GENERAL_SOUND = "dream"


def background_music(enabled):
    """Hidden looping music: general until a mood is known, then the mood's world.
    Silent while a Soundspace soundscape is playing, so two sounds never overlap."""
    if not enabled or st.session_state.get("now_playing"):
        return
    world = active_world()
    kind = sound_kind(world) if world is not None else GENERAL_SOUND
    with st.container(key="bg-music"):
        st.audio(world_sound(kind), format="audio/wav", loop=True, autoplay=True)
