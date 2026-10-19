# ORBIT
# Every feeling has a universe.
# A Class 12 CBSE Artificial Intelligence project.
#
# This is the main file of the app. Streamlit reads it from top to bottom
# and turns it into a web page. To run it, type in the terminal:
#     streamlit run app.py
#
# The project is split into small files:
#   app.py         -> page settings, navigation, choosing which page to show
#   views.py       -> one function per page (Home, Mood Lab, ...)
#   components.py  -> reusable pieces (planets, cards, saving worlds)
#   world_data.py  -> sample content, loaded from data/worlds.csv
#   styles.py      -> colours, fonts and layout (CSS)

import streamlit as st

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
load_css()

# ---------------------------------------------------------------
# 2. The app's memory (session state)
# These values survive button clicks, but reset on page refresh.
# ---------------------------------------------------------------
DEFAULTS = {
    "page": "Home",        # which page is open
    "collection": [],      # saved worlds
    "home_result": None,   # world shown after "Find my orbit"
    "lab_result": None,    # text sent to the Mood Lab
    "capsule": None,       # chosen capsule number
    "pack": None,          # creative pack from the vending machine
    "flash": None,         # short message to show as a pop-up toast
}
for name, value in DEFAULTS.items():
    if name not in st.session_state:
        st.session_state[name] = value

# Show a short message (for example "Saved Lavender Haze") once.
if st.session_state.flash:
    st.toast(st.session_state.flash)
    st.session_state.flash = None

# ---------------------------------------------------------------
# 3. Navigation
# Each label points to the function in views.py that draws that page.
# ---------------------------------------------------------------
PAGES = {
    "Home": views.home,
    "Mood Lab": views.mood_lab,
    "Vending Machine": views.vending_machine,
    "ORBIT": views.universe,
    "Soundspace": views.soundspace,
    "My Collection": views.collection,
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
