"""
ORBIT
Every feeling has a universe.

This is the main file of the app. Streamlit reads it from top to bottom and
turns it into a web page. To run it, type in the terminal:
    streamlit run app.py

Every visit opens on the landing page (landing.py): a small universe of
revolving planets that asks your name and age. After "Start Exploring Your
Universe" the app has 3 tabs:
    Create     -> Creator Mode (create_ui.py, spark_ui.py) and the Mood Studio (studio.py)
    Feel       -> check-in (today.py), chat (companion.py), Calm Room, stress busters, Reach Out, Mood Lab, ...
    My Galaxy  -> journal and galaxy (journal.py), Patterns, Wrapped (wrapped.py), saved worlds, collection
Settings live in the menu in the top right corner (settings_ui.py).

The AI parts live in analysis.py, emotion_model.py, orbit_head.py, hinglish.py,
explain.py, safety.py and llm.py. Data is saved by storage.py.
"""
import time

import streamlit as st

import calm_room
import companion
import create_ui
import demo_mode
import games
import journal
import landing
import letters
import onboarding
import patterns
import reach_out
import safety_plan
import settings_ui
import storage
import studio
import theme
import today
import vending
import views
import wrapped
from components import footer, go_to, top_bar
from styles import accessibility_css, load_css

st.set_page_config(page_title="ORBIT", page_icon="🪐", layout="wide", initial_sidebar_state="collapsed")
storage.init()
load_css(extra=calm_room.breathing_css() + accessibility_css(onboarding.accessibility_settings()))

DEFAULTS = {
    "page": "Home",
    "home_result": None,
    "today_done": False,
    "lab_result": None,
    "lab_explain": None,
    "chat": [],
    "chat_token_given": False,
    "tokens": 3,
    "now_playing": None,
    "flash": [],
    "creative": None,
    "create_pending": None,
    "create_offer": None,
    "create_break": None,
    "session_started": time.time(),
}
for name, value in DEFAULTS.items():
    if name not in st.session_state:
        st.session_state[name] = list(value) if isinstance(value, list) else value
if "collection" not in st.session_state:
    st.session_state.collection = storage.list_collection()

if not st.session_state.get("started"):
    landing.landing_page()
    st.stop()

PAGES = {
    "Create": ("Create", "Creative universe", create_ui.create_page),
    "Mood Studio": ("Create", "Quick palette & music", studio.studio_page),
    "Home": ("Feel", "Check-in", today.today_page),
    "Companion": ("Feel", "Talk to ORBIT", companion.companion_page),
    "Calm Room": ("Feel", "Calm Room", calm_room.calm_room_page),
    "Stress busters": ("Feel", "Stress busters", games.games_page),
    "Reach Out": ("Feel", "Reach Out", reach_out.reach_out_page),
    "Letters": ("Feel", "Letters", letters.letters_page),
    "Safety plan": ("Feel", "Safety plan", safety_plan.safety_plan_page),
    "Mood Lab": ("Feel", "Mood Lab", views.mood_lab),
    "Soundspace": ("Feel", "Soundspace", views.soundspace),
    "Vending Machine": ("Feel", "Arcade", vending.vending_machine),
    "Journal": ("My Galaxy", "Galaxy & journal", journal.journal_page),
    "Wrapped": ("My Galaxy", "Wrapped", wrapped.wrapped_page),
    "Patterns": ("My Galaxy", "Patterns", patterns.patterns_page),
    "ORBIT": ("My Galaxy", "Saved worlds", views.universe),
    "My Collection": ("My Galaxy", "Collection", views.collection),
}
TABS = ["Create", "Feel", "My Galaxy"]


def open_tab(tab):
    """Open a tab at the section the user last used there."""
    if tab in ("Create", "Feel"):
        storage.set_setting("last_mode", tab)
    remembered = st.session_state.get(f"last_{tab}")
    go_to(remembered or next(page for page, (t, _, _) in PAGES.items() if t == tab))


if st.session_state.page not in PAGES:
    st.session_state.page = "Home"
current_tab = PAGES[st.session_state.page][0]
st.session_state[f"last_{current_tab}"] = st.session_state.page

theme.background_music(settings_ui.music_on())

with st.container(key="topbar-row"):
    brand, menu = st.columns([5, 1], vertical_alignment="center")
    with brand:
        top_bar()
    with menu:
        settings_ui.settings_menu()
theme.world_bar()
demo_mode.banner()
with st.container(key="nav"):
    for column, tab in zip(st.columns(len(TABS)), TABS):
        label = tab
        if tab == "My Galaxy" and st.session_state.collection:
            label += f" · {len(st.session_state.collection)}"
        column.button(label, key=f"tab_{tab}", type="primary" if tab == current_tab else "secondary",
                      on_click=open_tab, args=(tab,))

sections = [(page, label) for page, (tab, label, _) in PAGES.items() if tab == current_tab]
if len(sections) > 1:
    with st.container(key="subnav"):
        for column, (page, label) in zip(st.columns(len(sections)), sections):
            column.button(label, key=f"nav_{page}", type="primary" if page == st.session_state.page else "secondary",
                          on_click=go_to, args=(page,))

PAGES[st.session_state.page][2]()
footer()

st.html(f"<style>{theme.theme_css(onboarding.accessibility_settings())}</style>")

for message in st.session_state.flash:
    st.toast(message)
st.session_state.flash = []
