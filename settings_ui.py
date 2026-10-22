"""
settings_ui.py
About -> Settings: accessibility, companion reply mode, demo mode, and your data
(download, import, Panic wipe).
"""
from datetime import date

import streamlit as st

import llm
import storage
from components import note, section_header
from onboarding import accessibility_toggles, save_toggle

REPLY_MODES = {
    "auto": "Automatic (best available)",
    "templates": "ORBIT templates (nothing leaves the device)",
    "local": "Local AI with Ollama (runs on this computer)",
    "cloud": "Cloud AI with Claude (your message is sent to Anthropic)",
}


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


def panic():
    """Delete everything immediately and start fresh."""
    storage.panic_wipe()
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.wiped = True


def panic_button(key):
    st.button("Panic wipe · delete everything now", key=key, type="primary", on_click=panic, width="stretch",
              help="Deletes your journal, saved worlds, ratings, corrections and settings immediately.")


def settings_page():
    section_header("Settings", "Make ORBIT yours",
                   "Accessibility, how replies are written, and full control over your data.", first=True)

    with st.container(key="glass-set-a11y"):
        st.html('<div class="eyebrow">Accessibility</div>')
        accessibility_toggles("set")
        note("Reduce motion also follows your device's own setting. The readability font is Lexend, which was "
             "designed to make reading easier; some dyslexic readers find it helps. (OpenDyslexic isn't "
             "available as a web font here.)")

    with st.container(key="glass-set-replies"):
        st.html('<div class="eyebrow">Companion replies</div>')
        st.radio("Who writes ORBIT's replies?", list(REPLY_MODES), format_func=REPLY_MODES.get,
                 index=list(REPLY_MODES).index(llm.chosen_mode()), key="set_reply_mode", on_change=save_reply_mode)
        if llm.cloud_key():
            st.toggle("I agree that my messages are sent to Anthropic to write replies", key="set_cloud",
                      value=llm.cloud_consent(), on_change=save_toggle, args=("cloud_ai_consent", "set_cloud"))
        else:
            st.html('<p class="body">Cloud AI is not set up (no API key in Streamlit secrets).</p>')
        st.html(f'<p class="body">Right now: <b>{llm.mode_label()}</b></p>')
        note("Whatever mode is chosen, crisis messages are never sent to any AI: they always get the fixed safety "
             "reply with helplines. AI replies are checked before they're shown, and fall back to templates.")

    with st.container(key="glass-set-games"):
        st.html('<div class="eyebrow">Stress-buster games</div>')
        st.toggle("Suggest a game when I'm stressed, anxious, sad or angry", key="set_games",
                  value=storage.get_setting("games_opt_out", "0") != "1", on_change=save_games)
        note("At most once per visit, never for happy or neutral feelings, and never in a crisis. All games are "
             "also in Tools → Stress busters.")

    with st.container(key="glass-set-demo"):
        st.html('<div class="eyebrow">Offline demo mode</div>')
        st.toggle("Use offline demo mode (no emotion model needed)", key="set_demo",
                  value=storage.get_setting("demo_mode", "0") == "1", on_change=save_toggle,
                  args=("demo_mode", "set_demo"))
        note("For presentations without internet. Sample sentences give real results saved earlier; other text "
             "gets a simpler offline estimate. ORBIT also switches to this automatically if the model can't load.")

    with st.container(key="glass-set-data"):
        st.html('<div class="eyebrow">Your data</div>')
        mode = storage.storage_mode()
        st.html('<p class="body">' + (
            "ORBIT is running online: data is kept only for <b>this browser session</b> and deleted within 24 hours. "
            "Download it to keep your journal, and import it next time."
            if mode == "session" else
            "Data is saved <b>only on this computer</b> (data/orbit.db). Downloading a copy is optional.") + "</p>")
        st.download_button("Download my data (.json)", storage.export_data(),
                           file_name=f"orbit_data_{date.today()}.json", mime="application/json", key="set_export")
        note("The downloaded file contains your journal text. Keep it somewhere private, and don't share it.")
        st.file_uploader("Import a file you downloaded before (replaces what's here now)", type=["json"],
                         key="set_import_file")
        st.button("Import", key="set_import", on_click=do_import)
        panic_button("set_panic")
