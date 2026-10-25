# ORBIT
# Every feeling has a universe.
# A Class 12 CBSE Artificial Intelligence project (SDG 3: Good Health and
# Well-being, SDG 4: Quality Education, SDG 10: Reduced Inequalities).
#
# This is the main file of the app. Streamlit reads it from top to bottom
# and turns it into a web page. To run it, type in the terminal:
#     streamlit run app.py
#
# ORBIT is a companion for creative people: it helps you feel okay and helps you make things.
# On opening, you choose Feel or Create (ORBIT remembers your last choice). The app has 4 tabs:
#   Create     -> Creator Mode (create_ui.py, spark_ui.py) and the Mood Studio (studio.py)
#   Feel       -> check-in (today.py), chat (companion.py), Calm Room, stress busters, Reach Out, Mood Lab, ...
#   My Galaxy  -> journal + emotion galaxy (journal.py), saved worlds and collection (views.py)
#   About      -> About ORBIT (about.py), AI Lab (ai_lab.py), Care & privacy (care.py), Settings (settings_ui.py)
#
# The AI parts live in analysis.py, emotion_model.py, orbit_head.py, hinglish.py,
# explain.py, safety.py and llm.py. Data is saved by storage.py.

import time

import streamlit as st

import about
import ai_lab
import calm_room
import care
import companion
import create_ui
import demo_mode
import games
import journal
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
from components import footer, go_to, top_bar
from styles import accessibility_css, load_css

# ---------------------------------------------------------------
# 1. Page settings (must be the first Streamlit command)
# ---------------------------------------------------------------
st.set_page_config(page_title="ORBIT", page_icon="🪐", layout="wide", initial_sidebar_state="collapsed")
storage.init()
load_css(extra=calm_room.breathing_css() + accessibility_css(onboarding.accessibility_settings()))

# ---------------------------------------------------------------
# 2. The app's memory for this browser tab (session state)
# ---------------------------------------------------------------
DEFAULTS = {
    "page": "Home",            # which page is open (see PAGES below)
    "home_result": None,       # today's check-in result
    "today_done": False,
    "lab_result": None,        # result shown in the Mood Lab
    "lab_explain": None,
    "chat": [],                # the Companion conversation
    "chat_token_given": False,
    "tokens": 3,               # arcade tokens
    "now_playing": None,       # Soundspace soundscape
    "flash": [],               # short pop-up messages to show once
    "creative": None,          # Creator Mode: the current creative universe and its history
    "create_pending": None,    # Creator Mode: an idea waiting for the optional quick questions
    "session_started": time.time(),
}
for name, value in DEFAULTS.items():
    if name not in st.session_state:
        st.session_state[name] = list(value) if isinstance(value, list) else value
if "collection" not in st.session_state:
    st.session_state.collection = storage.list_collection()

# ---------------------------------------------------------------
# 3. Onboarding and consent (first visit, or after a Panic wipe)
# ---------------------------------------------------------------
if st.session_state.pop("wiped", False):
    st.toast("Everything was deleted from this device.")
if onboarding.needs_onboarding():
    onboarding.onboarding_page()
    st.stop()

# ---------------------------------------------------------------
# 4. Navigation: 4 tabs, each with a few sections
# ---------------------------------------------------------------
PAGES = {   # page name -> (tab, label in that tab, function that draws it)
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
    "Patterns": ("My Galaxy", "Patterns", patterns.patterns_page),
    "ORBIT": ("My Galaxy", "Saved worlds", views.universe),
    "My Collection": ("My Galaxy", "Collection", views.collection),
    "About": ("About", "About ORBIT", about.about_page),
    "AI Lab": ("About", "AI Lab", ai_lab.ai_lab_page),
    "Care": ("About", "Care & privacy", care.care_page),
    "Settings": ("About", "Settings", settings_ui.settings_page),
}
TABS = ["Create", "Feel", "My Galaxy", "About"]
TAB_LABELS = {"Create": "Create", "Feel": "Feel", "My Galaxy": "My Galaxy", "About": "About & AI Lab"}


def open_tab(tab):
    """Open a tab at the section the user last used there."""
    if tab in ("Create", "Feel"):
        storage.set_setting("last_mode", tab)          # remembered for next time
    remembered = st.session_state.get(f"last_{tab}")
    go_to(remembered or next(page for page, (t, _, _) in PAGES.items() if t == tab))


def choose_mode(mode):
    st.session_state.mode_chosen = True
    open_tab(mode)


def mode_choice():
    """On opening: Feel or Create. The last choice is remembered and highlighted."""
    last = storage.get_setting("last_mode", "")
    top_bar()
    greeting = "Welcome back" if last else "Welcome"
    st.html(f'<div class="section-head first" style="text-align:center"><div class="eyebrow">{greeting}</div>'
            '<div class="display">What would you like to do?</div><p class="lede" style="margin:0 auto">ORBIT is '
            "a companion for creative people: it helps you feel okay and helps you make things.</p></div>")
    left, right = st.columns(2, gap="medium")
    for column, mode, text in ((left, "Feel", "Check in with how you feel, talk, breathe, play a stress buster."),
                               (right, "Create", "Turn an idea, a feeling or nothing at all into a creative universe.")):
        with column:
            st.html(f'<div class="mode-card"><b>{mode}</b><p>{text}</p>'
                    + ('<small>Your last choice</small>' if last == mode else "") + "</div>")
            st.button(f"Open {mode}", key=f"mode_{mode}", type="primary" if last == mode else "secondary",
                      on_click=choose_mode, args=(mode,), width="stretch")


if st.session_state.page not in PAGES:
    st.session_state.page = "Home"
if not st.session_state.get("mode_chosen"):
    if st.session_state.page == "Home":      # a fresh visit: ask Feel or Create
        mode_choice()
        st.stop()
    st.session_state.mode_chosen = True       # arrived on a specific page (e.g. a link inside the app)
current_tab = PAGES[st.session_state.page][0]
st.session_state[f"last_{current_tab}"] = st.session_state.page

top_bar()
theme.world_bar()
with st.container(key="quick-exit"):
    with st.popover("Panic wipe"):
        st.html('<p class="body">Deletes your journal, saved worlds, ratings, corrections and settings from this '
                "device <b>immediately</b>. This can't be undone.</p>")
        settings_ui.panic_button("top_panic")
demo_mode.banner()
with st.container(key="nav"):
    for column, tab in zip(st.columns(len(TABS)), TABS):
        label = TAB_LABELS[tab]
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

# ---------------------------------------------------------------
# 5. Show the chosen page
# ---------------------------------------------------------------
PAGES[st.session_state.page][2]()
footer()

# The world theme (feature B). Added last, so a feeling detected during this
# run changes the colours straight away.
st.html(f"<style>{theme.theme_css(onboarding.accessibility_settings())}</style>")

# Pop-up messages (e.g. "Saved Lavender Haze"). Shown last so messages
# created while drawing the page appear straight away.
for message in st.session_state.flash:
    st.toast(message)
st.session_state.flash = []
