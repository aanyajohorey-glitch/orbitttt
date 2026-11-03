"""
journal.py
The check-in history used by Patterns and Wrapped.

Every check-in is saved on this computer in data/orbit.db (see storage.py).
entries_table() turns those entries into a table; style() gives charts
ORBIT's look. DEMO_STORY holds sample sentences for offline demo mode.
"""
from datetime import datetime

import pandas as pd

import storage
from emotion_model import GROUP_OF, mood_score

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
FONT = "Manrope"


def entries_table():
    rows = []
    for entry in storage.list_entries():
        when = datetime.fromisoformat(entry["created_at"])
        rows.append({
            "id": entry["id"], "when": when, "date": when.date(), "weekday": WEEKDAYS[when.weekday()],
            "source": entry["source"], "text": entry["text"], "primary": entry["primary_emotion"],
            "score": entry["primary_score"], "family": GROUP_OF[entry["primary_emotion"]],
            "mood": mood_score(entry["emotions"]), "world": entry["world"], "demo": entry["demo"],
            "emotions": entry["emotions"],
        })
    return pd.DataFrame(rows)


DEMO_STORY = [
    "Pre-boards start next week and I can't stop worrying about maths.",
    "Couldn't sleep properly, my mind keeps racing about the exams.",
    "Had a fight with my brother and I'm so annoyed with everyone today.",
    "Studied for six hours, I'm exhausted but a bit proud of myself.",
    "I miss my old friends from my previous school so much.",
    "Got my chemistry practical done! Such a relief.",
    "Feeling nervous again, the physics paper is tomorrow.",
    "The physics paper went better than I expected, I'm so happy!",
    "My best friend surprised me with my favourite snacks, I love her.",
    "Kind of a normal day, nothing special happened.",
    "I wonder what I actually want to study in college.",
    "Thank you to my mom for staying up with me while I revised.",
    "Went for a walk in the evening and felt calm for the first time in weeks.",
    "Feeling hopeful about the results, whatever happens I tried my best.",
]


def style(chart):
    from onboarding import accessibility_settings
    night = accessibility_settings().get("night_mode")
    text, grid = ("#CFC8DE", "#3A3550") if night else ("#6B6773", "#ECE7F2")
    return (chart.configure(background="transparent", font=FONT)
            .configure_view(strokeWidth=0)
            .configure_axis(labelColor=text, titleColor=text, gridColor=grid,
                            domainColor=grid, tickColor=grid, labelFontSize=11, titleFontSize=11)
            .configure_legend(labelColor=text, titleColor=text, orient="bottom"))


