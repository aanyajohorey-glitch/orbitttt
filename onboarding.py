"""
onboarding.py
Accessibility settings (reduced motion, larger text, high contrast, readability
font, dark theme). They are changed in the Settings menu (settings_ui.py).
"""
import streamlit as st

import storage

A11Y_OPTIONS = {
    "reduced_motion": "Reduce motion (no animations)",
    "large_text": "Larger text",
    "high_contrast": "High contrast",
    "readable_font": "Readability font (Lexend)",
    "night_mode": "Night mode (dark theme)",
}


def accessibility_settings():
    return {key: storage.get_setting(f"a11y_{key}", "0") == "1" for key in A11Y_OPTIONS}


def reduced_motion():
    """True when the user switched on "Reduce motion" (the device setting is handled in CSS)."""
    return accessibility_settings()["reduced_motion"]


def save_toggle(setting, key):
    storage.set_setting(setting, "1" if st.session_state[key] else "0")
