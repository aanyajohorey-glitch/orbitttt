"""
landing.py
The first page: a calm ivory hero with a small planetary illustration, the
ORBIT wordmark, and a card that asks the visitor's name and age, then
"Start Exploring Your Universe".

The name and age are saved only on this device (in the settings table).
"""
import streamlit as st

import storage

PLANETS = [
    ("lp-p-lavender", "#F1EBFA", "#C9B9E8", "#A895D2", True),
    ("lp-p-blush", "#FBEFF3", "#EBCBD7", "#C695AA", False),
    ("lp-p-sage", "#EEF3EB", "#C7D3C0", "#98AA8C", False),
    ("lp-p-dot", "#F6EFF7", "#E6DCF6", "#C9B9E8", False),
]
SPARKLES = [(14, 18, 0), (82, 12, 1.2), (90, 58, 2.4), (8, 72, 0.8), (60, 88, 1.8), (36, 6, 3.0)]


def universe_html():
    """The planetary illustration (plain divs, because st.html removes inline SVG)."""
    planets = []
    for name, light, mid, dark, ring in PLANETS:
        ring_html = '<i class="lp-ring"></i>' if ring else ""
        planets.append(f'<div class="lp-planet {name}" style="--c0:{light};--c1:{mid};--c2:{dark}">{ring_html}</div>')
    sparkles = "".join(f'<i class="lp-spark" style="left:{x}%;top:{y}%;animation-delay:{d}s"></i>'
                       for x, y, d in SPARKLES)
    return ('<div class="lp-art"><div class="lp-path lp-path-1"></div><div class="lp-path lp-path-2"></div>'
            + "".join(planets) + sparkles + "</div>")


def hero_html():
    return ('<div class="lp-hero"><div class="lp-eyebrow">A creative companion for how you feel</div>'
            '<div class="lp-wordmark">ORBIT</div>'
            '<div class="lp-tagline">Every feeling has a universe.</div>'
            '<p class="lp-sub">Turn your emotions into colours, sounds and worlds.</p></div>')


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
    saved_age = storage.get_setting("age", "")
    with st.container(key="landing"):
        words, art = st.columns([1.05, 1], gap="large", vertical_alignment="center")
        with art:
            st.html(universe_html())
        with words:
            st.html(hero_html())
            with st.container(key="landing-form"):
                st.text_input("Your name", key="landing_name", value=storage.get_setting("name", ""), max_chars=30,
                              placeholder="Your name or a nickname")
                st.number_input("Your age", key="landing_age", min_value=5, max_value=100, step=1,
                                value=int(saved_age) if saved_age.isdigit() else None, placeholder="Your age")
                st.button("Start Exploring Your Universe", key="landing_start", type="primary", on_click=start,
                          width="stretch")
            st.html('<p class="lp-note">ORBIT is an AI companion, not a therapist. If you are ever in danger, '
                    "call 112 or Tele-MANAS on 14416.</p>")
