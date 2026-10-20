"""
nudges.py
Dependence nudges: ORBIT should support people, not replace people.

ORBIT gently suggests talking to a real person when:
  - a session has been long (30+ minutes, or 16+ chat messages), or
  - there have been 3 or more low-mood check-ins in the last 7 days.

Each nudge shows at most once per session and can be dismissed.
"""
import time
from datetime import datetime, timedelta

import streamlit as st

import storage
from emotion_model import GROUP_OF

LONG_SESSION_MINUTES = 30
LONG_CHAT_MESSAGES = 16
LOW_MOOD_CHECKINS = 3
LOW_FAMILIES = {"Sadness", "Fear", "Anger"}


def low_mood_count(days=7):
    since = (datetime.now() - timedelta(days=days)).isoformat(timespec="seconds")
    return sum(1 for e in storage.list_entries()
               if not e["demo"] and e["created_at"] >= since and GROUP_OF.get(e["primary_emotion"]) in LOW_FAMILIES)


def nudge_reason():
    """Which nudge applies right now, if any: 'low_mood', 'long_session' or None."""
    if low_mood_count() >= LOW_MOOD_CHECKINS:
        return "low_mood"
    minutes = (time.time() - st.session_state.get("session_started", time.time())) / 60
    if minutes >= LONG_SESSION_MINUTES or len(st.session_state.get("chat", [])) >= LONG_CHAT_MESSAGES:
        return "long_session"
    return None


MESSAGES = {
    "low_mood": ("A gentle check-in from ORBIT",
                 "You've had a few heavy days this week. You don't have to carry that alone. Talking to someone "
                 "you trust (a parent, a teacher, a school counsellor or a friend) can really help. Tele-MANAS "
                 "(14416) is also free and confidential, any time."),
    "long_session": ("Time for a real-world break?",
                     "We've been talking for a while. ORBIT is happy to listen, but people can support you in ways "
                     "an app can't. Maybe message a friend, step outside, or tell someone at home how you're doing."),
}


def dismiss(reason):
    st.session_state.setdefault("nudges_dismissed", set()).add(reason)


def nudge_card(result=None):
    if result is not None and result.get("safety") == "crisis":
        return  # the crisis card already points to people
    reason = nudge_reason()
    if not reason or reason in st.session_state.get("nudges_dismissed", set()):
        return
    title, text = MESSAGES[reason]
    with st.container(key="glass-nudge"):
        st.html(f'<div class="eyebrow">{title}</div><p class="body" style="margin-top:.3rem">{text}</p>')
        st.button("Okay, thank you", key=f"nudge_ok_{reason}", type="tertiary", on_click=dismiss, args=(reason,))
