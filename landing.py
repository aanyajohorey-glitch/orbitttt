"""
landing.py
The first page: a small universe with planets revolving around a glowing core,
a card that asks the visitor's name and age, and "Start Exploring Your Universe".

The name and age are saved only on this device (in the settings table). Clicking
the button also counts as the visitor's first tap, which lets the background
music start (browsers block sound that starts before any tap).
"""
import streamlit as st

import storage

ORBITS = [  # (orbit size in px, seconds per turn, planet size, light colour, dark colour, ring?)
    (300, 28, 26, "#F6E1E9", "#C695AA", False),
    (430, 46, 38, "#DCE5F7", "#7F93BF", True),
    (560, 70, 30, "#E2EADC", "#98AA8C", False),
    (690, 98, 46, "#F6E7CC", "#CDAA78", True),
]


def universe_html():
    rings = []
    for i, (size, seconds, planet, light, dark, ring) in enumerate(ORBITS):
        ring_html = '<i class="lp-ring"></i>' if ring else ""
        rings.append(
            f'<div class="lp-orbit" style="--s:{size}px;--t:{seconds}s;--d:-{seconds * (0.1 + i * 0.23):.1f}s">'
            f'<div class="lp-planet" style="--p:{planet}px;--c1:{light};--c2:{dark}">{ring_html}</div></div>')
    return ('<div class="lp-sky"><div class="lp-stars"></div><div class="lp-stars lp-stars-2"></div>'
            '<div class="lp-system">' + "".join(rings) + '<div class="lp-core"></div></div>'
            '<div class="lp-title"><div class="lp-wordmark">ORBIT</div>'
            '<div class="lp-tagline">Every feeling has a universe.</div></div></div>')


def start():
    name = st.session_state.get("landing_name", "").strip()
    age = st.session_state.get("landing_age")
    if name:
        storage.set_setting("name", name)
    if age:
        storage.set_setting("age", str(int(age)))
    storage.set_setting("onboarded", "1")
    st.session_state.started = True
    last = storage.get_setting("last_mode", "Create")
    st.session_state.page = "Create" if last == "Create" else "Home"


def landing_page():
    st.html(universe_html())
    saved_age = storage.get_setting("age", "")
    with st.container(key="landing-form"):
        st.html('<div class="lp-ask">Who is exploring today?</div>')
        st.text_input("Your name", key="landing_name", value=storage.get_setting("name", ""), max_chars=30,
                      placeholder="Your name or a nickname")
        st.number_input("Your age", key="landing_age", min_value=5, max_value=100, step=1,
                        value=int(saved_age) if saved_age.isdigit() else None, placeholder="Your age")
        st.button("Start Exploring Your Universe", key="landing_start", type="primary", on_click=start,
                  width="stretch")
        st.html('<p class="lp-note">ORBIT is an AI companion, not a therapist. If you are ever in danger, call '
                "112 or Tele-MANAS on 14416.</p>")
