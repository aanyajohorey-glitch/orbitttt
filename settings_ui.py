"""
settings_ui.py
The Settings menu in the top right corner: display (high contrast, dark theme,
larger text, readability font, reduced motion), background music, how replies
are written, demo mode, and your data (download and import).
"""
from datetime import date

import streamlit as st

import llm
import storage
from onboarding import A11Y_OPTIONS, accessibility_settings, save_toggle

REPLY_MODES = {
    "auto": "Automatic (best available)",
    "templates": "ORBIT templates (nothing leaves the device)",
    "local": "Local AI with Ollama (runs on this computer)",
    "cloud": "Cloud AI with Claude (your message is sent to Anthropic)",
}
DISPLAY_LABELS = {
    "high_contrast": "High contrast",
    "night_mode": "Dark theme",
    "large_text": "Larger text",
    "readable_font": "Readability font",
    "reduced_motion": "Reduce motion",
}


def music_on():
    return storage.get_setting("bg_music", "1") == "1"


def save_reply_mode():
    storage.set_setting("reply_mode", st.session_state.set_reply_mode)


def save_games():
    storage.set_setting("games_opt_out", "0" if st.session_state.set_games else "1")


def do_import():
    upload = st.session_state.get("set_import_file")
    if upload is None:
        return
    try:
        count = storage.import_data(upload.getvalue())
        st.session_state.collection = storage.list_collection()
        st.session_state.flash.append(f"Imported {count} saved items.")
    except Exception as error:
        st.session_state.flash.append(f"That file couldn't be imported: {error}")


def heading(text):
    st.html(f'<div class="set-head">{text}</div>')


def settings_menu():
    """Everything that can be changed, inside one popover."""
    with st.popover("⚙ Settings"):
        heading("Display")
        current = accessibility_settings()
        for key in DISPLAY_LABELS:
            if key in A11Y_OPTIONS:
                st.toggle(DISPLAY_LABELS[key], value=current[key], key=f"set_{key}", on_change=save_toggle,
                          args=(f"a11y_{key}", f"set_{key}"))

        heading("Sound")
        st.toggle("Background music", value=music_on(), key="set_bg_music", on_change=save_toggle,
                  args=("bg_music", "set_bg_music"),
                  help="A calm general soundscape, which changes to match your mood once ORBIT knows it.")

        heading("Companion replies")
        st.selectbox("Who writes ORBIT's replies?", list(REPLY_MODES), format_func=REPLY_MODES.get,
                     index=list(REPLY_MODES).index(llm.chosen_mode()), key="set_reply_mode",
                     on_change=save_reply_mode)
        if llm.cloud_key():
            st.toggle("I agree that my messages are sent to Anthropic to write replies", key="set_cloud",
                      value=llm.cloud_consent(), on_change=save_toggle, args=("cloud_ai_consent", "set_cloud"))
        st.caption("Crisis messages are never sent to any AI: they always get the fixed safety reply with helplines.")

        heading("Extras")
        st.toggle("Suggest a game when I'm stressed or low", key="set_games",
                  value=storage.get_setting("games_opt_out", "0") != "1", on_change=save_games)
        st.toggle("Offline demo mode", key="set_demo", value=storage.get_setting("demo_mode", "0") == "1",
                  on_change=save_toggle, args=("demo_mode", "set_demo"))

        heading("Your data")
        st.caption("Online, data is kept only for this browser session. Download it to keep your journal."
                   if storage.storage_mode() == "session" else "Data is saved only on this computer.")
        st.download_button("Download my data (.json)", storage.export_data(),
                           file_name=f"orbit_data_{date.today()}.json", mime="application/json", key="set_export",
                           width="stretch")
        st.file_uploader("Import a file you downloaded before", type=["json"], key="set_import_file")
        st.button("Import", key="set_import", on_click=do_import)
