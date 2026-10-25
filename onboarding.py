"""
onboarding.py
The first screen: what ORBIT is and isn't, what it stores, and consent.

Shown on the first visit (and again after a Panic Wipe, or every new browser
session when ORBIT runs on Streamlit Cloud, because nothing is kept there).
"""
import streamlit as st

import llm
import storage
from components import esc, planet_html
from safety import helplines_html

A11Y_OPTIONS = {
    "reduced_motion": "Reduce motion (no animations)",
    "large_text": "Larger text",
    "high_contrast": "High contrast",
    "readable_font": "Readability font (Lexend)",
    "night_mode": "Night mode (dark theme)",
}


def needs_onboarding():
    return storage.get_setting("onboarded", "0") != "1"


def accessibility_settings():
    return {key: storage.get_setting(f"a11y_{key}", "0") == "1" for key in A11Y_OPTIONS}


def reduced_motion():
    """True when the user switched on "Reduce motion" (the device setting is handled in CSS)."""
    return accessibility_settings()["reduced_motion"]


def save_toggle(setting, key):
    storage.set_setting(setting, "1" if st.session_state[key] else "0")


def accessibility_toggles(prefix):
    current = accessibility_settings()
    for key, label in A11Y_OPTIONS.items():
        st.toggle(label, value=current[key], key=f"{prefix}_{key}", on_change=save_toggle,
                  args=(f"a11y_{key}", f"{prefix}_{key}"))


def start():
    storage.set_setting("onboarded", "1")
    name = st.session_state.get("onb_name", "").strip()
    if name:
        storage.set_setting("name", name)
    if llm.cloud_key():
        storage.set_setting("cloud_ai_consent", "1" if st.session_state.get("onb_cloud") else "0")


def where_data_lives():
    if storage.storage_mode() == "session":
        return ("ORBIT is running online, so your check-ins are kept <b>only for this browser session</b> on the "
                "server and deleted within 24 hours. Nobody else can see them. To keep your journal, use "
                "<b>About → Settings → Download my data</b>, and import it next time.")
    return ("Your check-ins, journal and settings are saved <b>only on this computer</b> (in data/orbit.db). "
            "Nothing is uploaded. You can download or delete everything at any time, including with one "
            "<b>Panic wipe</b> button at the top of every page.")


def onboarding_page():
    st.html(
        '<div class="onboarding-hero">'
        + planet_html("#E6DCF6", "#A895D2", 96, ring=True)
        + '<div class="wordmark" style="font-size:clamp(2.6rem,7vw,4rem)">ORBIT</div>'
        '<div class="tagline">Every feeling has a universe.</div></div>'
    )
    with st.container(key="glass-onboarding"):
        st.html(
            '<div class="eyebrow">Before we begin</div>'
            '<div class="title-sm" style="font-size:1.8rem">A few honest things about ORBIT</div>'
            '<div class="onb-points">'
            '<div class="onb-point"><b>ORBIT is an AI, not a therapist.</b><p class="body">It can help you name '
            "a feeling and try a small coping exercise. It can't diagnose anything, and it is not for "
            "emergencies. Real people can help in ways an app can't.</p></div>"
            f'<div class="onb-point"><b>What is stored</b><p class="body">{where_data_lives()}</p></div>'
            '<div class="onb-point"><b>No personal details needed</b><p class="body">No account, no email, no '
            "phone number. A name is optional. Please don't write other people's names or private details.</p></div>"
            '<div class="onb-point"><b>Under 18?</b><p class="body">It\'s a good idea to let a parent, guardian or '
            "teacher know you're using ORBIT, so someone you trust is in the loop.</p></div>"
            "</div>"
        )
        st.html('<div class="field-label" style="margin-top:1rem">If you ever need help right now</div>'
                + helplines_html())

    with st.container(key="glass-onboarding-setup"):
        st.text_input("What should ORBIT call you? (optional)", key="onb_name", max_chars=30,
                      placeholder="A first name or a nickname, or leave blank")
        if llm.cloud_key():
            st.checkbox("Let ORBIT send my messages to Anthropic's Claude AI to write warmer replies (optional). "
                        "Without this, replies are written on the server by ORBIT's own templates.", key="onb_cloud")
        st.html('<div class="field-label" style="margin-top:.6rem">Make ORBIT easier to use (you can change '
                "these later in About → Settings)</div>")
        left, right = st.columns(2)
        options = list(A11Y_OPTIONS.items())
        current = accessibility_settings()
        for i, (key, label) in enumerate(options):
            column = left if i % 2 == 0 else right
            column.toggle(label, value=current[key], key=f"onb_{key}", on_change=save_toggle,
                          args=(f"a11y_{key}", f"onb_{key}"))
        agreed = st.checkbox("I understand that ORBIT is an AI and not a replacement for real help", key="onb_agree")
        st.button("Start ORBIT", key="onb_start", type="primary", disabled=not agreed, on_click=start)
    st.html(f'<p class="body" style="text-align:center;margin-top:1rem">{esc("A Class 12 CBSE AI project.")}</p>')
