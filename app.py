# ORBIT
# Every feeling has a universe.
# A Class 12 CBSE Artificial Intelligence project (SDG 3: Good Health and
# Well-being, SDG 4: Quality Education, SDG 10: Reduced Inequalities).
#
# This is the main file of the app. Streamlit reads it from top to bottom
# and turns it into a web page. To run it, type in the terminal:
#     streamlit run app.py
#
# How the project is organised:
#   app.py          -> page settings, navigation, choosing which page to show
#   views.py        -> Home, Mood Lab, ORBIT Universe, Soundspace, My Collection
#   companion.py    -> the Companion chat and how replies are written
#   calm_room.py    -> breathing, grounding, thought reframe, gratitude jar
#   journal.py      -> mood journal, charts, insights and the emotion galaxy
#   vending.py      -> the arcade vending machine
#   ai_lab.py       -> evaluation, impact study and model card
#   care.py         -> safety, helplines and privacy controls
#   analysis.py     -> the AI pipeline shared by every page
#   emotion_model.py, hinglish.py, explain.py, safety.py -> the AI parts
#   storage.py      -> saving data on this computer (SQLite)
#   soundscapes.py, voice.py, components.py, styles.py, world_data.py -> helpers

import streamlit as st

import ai_lab
import calm_room
import care
import companion
import journal
import storage
import vending
import views
from components import footer, go_to, top_bar
from styles import load_css

# ---------------------------------------------------------------
# 1. Page settings (must be the first Streamlit command)
# ---------------------------------------------------------------
st.set_page_config(
    page_title="ORBIT",
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="collapsed",
)
load_css(extra=calm_room.breathing_css())
storage.init()

# ---------------------------------------------------------------
# 2. The app's memory for this browser tab (session state)
# ---------------------------------------------------------------
DEFAULTS = {
    "page": "Home",            # which page is open
    "home_result": None,       # result shown after "Find my orbit"
    "lab_result": None,        # result shown in the Mood Lab
    "lab_explain": None,       # "why" explanation for the Mood Lab result
    "chat": [],                # the Companion conversation
    "chat_token_given": False,
    "tokens": 3,               # arcade tokens for the Vending Machine
    "now_playing": None,       # Soundspace soundscape
    "flash": [],               # short pop-up messages to show once
}
for name, value in DEFAULTS.items():
    if name not in st.session_state:
        st.session_state[name] = list(value) if isinstance(value, list) else value
if "collection" not in st.session_state:
    st.session_state.collection = storage.list_collection()   # saved worlds from the database

# ---------------------------------------------------------------
# 3. Navigation
# Each label points to the function that draws that page.
# ---------------------------------------------------------------
PAGES = {
    "Home": views.home,
    "Companion": companion.companion_page,
    "Mood Lab": views.mood_lab,
    "Calm Room": calm_room.calm_room_page,
    "Journal": journal.journal_page,
    "Vending Machine": vending.vending_machine,
    "ORBIT": views.universe,
    "Soundspace": views.soundspace,
    "My Collection": views.collection,
    "AI Lab": ai_lab.ai_lab_page,
    "Care": care.care_page,
}

top_bar()
with st.container(key="nav"):
    columns = st.columns(len(PAGES))
    for column, label in zip(columns, PAGES):
        shown = label
        if label == "My Collection" and st.session_state.collection:
            shown = f"My Collection · {len(st.session_state.collection)}"
        column.button(
            shown,
            key=f"nav_{label}",
            type="primary" if st.session_state.page == label else "secondary",
            on_click=go_to,
            args=(label,),
        )

# ---------------------------------------------------------------
# 4. Show the chosen page
# ---------------------------------------------------------------
PAGES[st.session_state.page]()

footer()

# Show queued pop-up messages (e.g. "Saved Lavender Haze", "+1 arcade token").
# This runs LAST so messages created while drawing the page appear straight away.
for message in st.session_state.flash:
    st.toast(message)
st.session_state.flash = []
