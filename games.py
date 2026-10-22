"""
games.py
Stress-buster games, offered ONLY when they might help.

When is a game offered? (offer_reason returns None when it should be)
  - The main feeling is a distress-type emotion (DISTRESS below), and
  - ORBIT is sure enough (not "unsure": then it asks a clarifying question first), and
  - it is NOT a crisis or a "concern" message (those get the safety flow), and
  - low moods are NOT repeating (then ORBIT suggests a real person instead), and
  - no game was offered yet in this browser session, and
  - the user hasn't chosen "Don't suggest games" (remembered on this device).
Joy, warmth, wonder and neutral feelings never trigger a game.

Each game is a small HTML/JavaScript file in the games/ folder, shown with
st.components.v1.html (a sandboxed frame). Games take 2-5 minutes and have no
scores, streaks or timers that pressure you.
"""
import json
import random
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

import storage
from emotion_model import GROUP_COLOURS, GROUP_OF
from world_data import get_world

GAMES_DIR = Path(__file__).parent / "games"

# Rules of thumb, kept in one place so they are easy to explain and change.
# GoEmotions has no "anxiety" label: nervousness and fear cover it. "annoyance" is mild anger.
# Grief is left out on purpose: heavy loss deserves people, not games.
DISTRESS = {"nervousness", "fear", "sadness", "anger", "annoyance", "disappointment"}
REPEATED_LOW_MOODS = 3        # this many low-mood check-ins in 7 days -> suggest a person, not a game

GAMES = {   # key: (title, what it helps with, file, minutes)
    "pop_worry": ("Pop the Worry", "Anxious thoughts", "pop_the_worry.html", "2-3"),
    "orb_flow": ("Orb Flow", "Feeling anxious or overwhelmed", "orb_flow.html", "3-5"),
    "zen_sand": ("Zen Sand Garden", "Feeling sad or tired", "zen_sand.html", "2-5"),
    "constellation": ("Constellation Connect", "Feeling restless", "constellation_connect.html", "2-4"),
    "planet_builder": ("Planet Builder", "Feeling sad or low", "planet_builder.html", "2-4"),
    "tiny_wins": ("Tiny Wins Quest", "Low energy", "tiny_wins.html", "2-5"),
    "crack_glass": ("Crack the Glass", "Feeling angry", "crack_the_glass.html", "2-3"),
    "mandala": ("Mandala Colouring", "Feeling stressed", "mandala.html", "3-5"),
    "rhythm": ("Rhythm Pulse", "Feeling tense", "rhythm_pulse.html", "2-3"),
}
FOR_EMOTION = {   # which games suit which feeling
    "nervousness": ["pop_worry", "orb_flow", "rhythm"],
    "fear": ["orb_flow", "pop_worry", "constellation"],
    "sadness": ["zen_sand", "planet_builder", "tiny_wins"],
    "disappointment": ["planet_builder", "tiny_wins", "mandala"],
    "anger": ["crack_glass", "rhythm"],
    "annoyance": ["crack_glass", "rhythm", "mandala"],
}


# ---------------------------------------------------------------
# Should a game be offered?
# ---------------------------------------------------------------
def opted_out():
    return storage.get_setting("games_opt_out", "0") == "1"


def offer_reason(result):
    """Why NOT to offer a game (a short reason), or None if a game may be offered."""
    if result is None:
        return "no result"
    if result.get("safety") == "crisis":
        return "crisis"              # the safety flow only
    if result.get("safety") == "concern":
        return "intense"             # a gentle note and real people, not games
    if result["final"]["emotion"] not in DISTRESS:
        return "not distress"
    if result["final"].get("unsure"):
        return "unsure"              # ask the clarifying question first
    from nudges import low_mood_count   # local import keeps this module light
    if low_mood_count() >= REPEATED_LOW_MOODS:
        return "repeated low mood"
    if opted_out():
        return "opted out"
    if st.session_state.get("game_offered"):
        return "already offered"
    return None


def pick_game(emotion):
    choices = FOR_EMOTION.get(emotion, ["orb_flow"])
    return random.choice(choices)


# ---------------------------------------------------------------
# The pop-up
# ---------------------------------------------------------------
def _play(key):
    st.session_state.game_playing = key


def _not_now():
    st.session_state.game_playing = None


def _never():
    storage.set_setting("games_opt_out", "1")
    st.session_state.game_playing = None
    st.session_state.flash.append("Okay, ORBIT won't suggest games. You can turn them back on in Settings.")


@st.dialog("A stress buster for you")
def offer_dialog(key):
    title, helps, _, minutes = GAMES[key]
    st.html(f'<p class="body" style="font-size:1rem">We found a stress buster game for you. Would you like to play?</p>'
            f'<div class="game-offer"><b>{title}</b><span>{helps} · about {minutes} minutes · no scores</span></div>')
    a, b, c = st.columns(3)
    if a.button("Play", key="game_play", type="primary", width="stretch", on_click=_play, args=(key,)):
        st.rerun()
    if b.button("Not now", key="game_later", width="stretch", on_click=_not_now):
        st.rerun()
    if c.button("Don't suggest games", key="game_never", type="tertiary", width="stretch", on_click=_never):
        st.rerun()


def maybe_offer(result):
    """Show the pop-up at most once per session, only when offer_reason allows it."""
    if offer_reason(result) is None:
        st.session_state.game_offered = True
        offer_dialog(pick_game(result["final"]["emotion"]))


# ---------------------------------------------------------------
# Showing a game
# ---------------------------------------------------------------
def palette_for(result=None):
    """Colours for a game: the feeling's world palette, or ORBIT's lavender."""
    world = get_world(result["world"]) if result and result.get("world") else None
    if world:
        colours, ink = world["palette"][:3], world["planet_dark"]
    elif result:
        light, ink = GROUP_COLOURS[GROUP_OF[result["final"]["emotion"]]]
        colours = [light, "#B9C8EA", "#EBCBD7"]
    else:
        colours, ink = ["#C9B9E8", "#B9C8EA", "#EBCBD7"], "#A895D2"
    return colours, ink


def game_html(key, palette, ink, reduced):
    """Put a game file together with the shared style and its colours."""
    _, _, filename, _ = GAMES[key]
    shared = (GAMES_DIR / "_shared.css").read_text(encoding="utf-8")
    body = (GAMES_DIR / filename).read_text(encoding="utf-8")
    settings = (f"const PALETTE = {json.dumps(palette)}; const INK = {json.dumps(ink)}; "
                f"const REDUCED = {'true' if reduced else 'false'} || "
                "window.matchMedia('(prefers-reduced-motion: reduce)').matches;")
    return ("<!doctype html><html><head><meta charset='utf-8'>"
            "<link href='https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500"
            "&family=Manrope:wght@400;600&display=swap' rel='stylesheet'>"
            f"<style>:root {{ --a: {palette[0]}; --b: {palette[1]}; --c: {palette[2]}; --ink: {ink}; }}\n{shared}</style>"
            f"<script>{settings}</script></head><body>{body}</body></html>")


def play(key, result=None, height=620):
    from onboarding import reduced_motion
    palette, ink = palette_for(result)
    components.html(game_html(key, palette, ink, reduced_motion()), height=height, scrolling=False)


def game_card(result):
    """In Today: the game the user chose to play, inside a card."""
    key = st.session_state.get("game_playing")
    if not key:
        return
    with st.container(key="glass-game"):
        title = GAMES[key][0]
        st.html(f'<div class="eyebrow">Stress buster · {title}</div>')
        play(key, result)
        st.button("I'm done", key="game_done", on_click=_not_now)


# ---------------------------------------------------------------
# Feel -> Stress busters: every game, any time
# ---------------------------------------------------------------
def games_page():
    from components import note, section_header
    section_header("Stress busters", "Small games for big feelings",
                   "Nine gentle games, 2-5 minutes each. No scores, no streaks, no pressure.", first=True)
    keys = list(GAMES)
    choice = st.pills("Choose a game", keys, format_func=lambda k: GAMES[k][0], key="games_pick") or keys[0]
    title, helps, _, minutes = GAMES[choice]
    st.html(f'<p class="body" style="margin:.2rem 0 .8rem">Good for: <b>{helps}</b> · about {minutes} minutes</p>')
    with st.container(key="glass-games"):
        play(choice, st.session_state.get("home_result"))
    note("Games are for everyday stress. If you're struggling a lot, or feel unsafe, please talk to someone you "
         "trust or call Tele-MANAS on 14416 (free, any time).")
