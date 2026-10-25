"""
patterns.py
My Galaxy -> Patterns: what your check-ins show over 7 days, 14 days, 30 days or a year.

    how often each feeling family appeared   (bar chart)
    a mood line over time                    (one point per day)
    a calendar heatmap                       (each day coloured by its average mood)
    bright days vs low days, and the weekdays / times of day when low moods cluster

Wording is always "a pattern we noticed": ORBIT never diagnoses.
If low moods are frequent, suggestions come in layers: (1) tools and games,
(2) the Reach Out Helper, (3) if it lasts about two weeks, a gentle suggestion
to talk to a trusted adult or counsellor, with Tele-MANAS.
"""
from datetime import datetime, timedelta

import altair as alt
import pandas as pd
import streamlit as st

from components import esc, go_to, note, section_header
from journal import WEEKDAYS, entries_table, style

# ---------------------------------------------------------------
# Rules of thumb. These numbers are NOT clinical thresholds: they were chosen
# by the student and should be reviewed by a school counsellor before real use.
# ---------------------------------------------------------------
RANGES = {"7 days": 7, "14 days": 14, "30 days": 30, "1 year": 365}
MIN_DAYS = {7: 3, 14: 5, 30: 7, 365: 14}   # days with check-ins needed before showing patterns
LOW_DAY_BELOW = -0.2                      # a day whose average mood is below this counts as a low day
BRIGHT_DAY_ABOVE = 0.2                    # ... above this counts as a bright day
FREQUENT_LOW_SHARE = 0.4                  # low days are "frequent" if they are 40% or more of check-in days
FREQUENT_LOW_MIN = 3                      # ... and there are at least 3 of them
PERSIST_WINDOW = 7                        # "lasting about two weeks": low days in BOTH of the last two weeks
PERSIST_MIN_PER_WINDOW = 2                # ... at least 2 low days in each of those weeks
PARTS_OF_DAY = [(5, "Morning"), (12, "Afternoon"), (17, "Evening"), (21, "Night")]


def part_of_day(hour):
    label = "Night"
    for start, name in PARTS_OF_DAY:
        if hour >= start:
            label = name
    return label


def in_range(table, days, now=None):
    now = now or datetime.now()
    if table.empty:
        return table
    return table[table["when"] >= now - timedelta(days=days)].copy()


def daily(table):
    """One row per day: average mood and the main feeling family."""
    if table.empty:
        return pd.DataFrame(columns=["date", "mood", "family", "checkins", "kind"])
    days = table.groupby("date").agg(mood=("mood", "mean"), checkins=("mood", "size"),
                                     family=("family", lambda f: f.value_counts().index[0])).reset_index()
    days["kind"] = days["mood"].apply(lambda m: "low" if m < LOW_DAY_BELOW else "bright" if m > BRIGHT_DAY_ABOVE
                                      else "in-between")
    return days


def enough_data(table, days):
    return table["date"].nunique() >= MIN_DAYS[days] if not table.empty else False


def low_pattern(days_table, now=None):
    """Which layer of suggestions applies: 0 = none, 1-2 = frequent low days, 3 = lasting about two weeks."""
    if days_table.empty:
        return 0
    low = days_table[days_table["kind"] == "low"]
    frequent = len(low) >= FREQUENT_LOW_MIN and len(low) / len(days_table) >= FREQUENT_LOW_SHARE
    if not frequent:
        return 0
    today = (now or datetime.now()).date()
    recent = sum(1 for d in low["date"] if today - d < timedelta(days=PERSIST_WINDOW))
    before = sum(1 for d in low["date"] if PERSIST_WINDOW <= (today - d).days < 2 * PERSIST_WINDOW)
    return 3 if recent >= PERSIST_MIN_PER_WINDOW and before >= PERSIST_MIN_PER_WINDOW else 2


def low_clusters(table):
    """Where low check-ins cluster: (weekday, count) and (part of day, count), most first."""
    low = table[table["mood"] < LOW_DAY_BELOW]
    if low.empty:
        return [], []
    weekdays = low["weekday"].value_counts()
    parts = low["when"].apply(lambda w: part_of_day(w.hour)).value_counts()
    return list(weekdays.items()), list(parts.items())


# ---------------------------------------------------------------
# Charts
# ---------------------------------------------------------------
def family_bars(table):
    counts = table["family"].value_counts().reset_index()
    counts.columns = ["family", "check-ins"]
    from emotion_model import GROUP_COLOURS
    families = list(GROUP_COLOURS)
    chart = alt.Chart(counts).mark_bar(cornerRadius=6).encode(
        y=alt.Y("family:N", sort="-x", title=None), x=alt.X("check-ins:Q", title="Check-ins", axis=alt.Axis(tickMinStep=1)),
        color=alt.Color("family:N", legend=None, scale=alt.Scale(domain=families,
                                                                 range=[GROUP_COLOURS[f][1] for f in families])),
        tooltip=["family", "check-ins"])
    return style(chart.properties(height=max(120, 28 * len(counts))))


def mood_line(days_table):
    data = days_table.copy()
    data["date"] = pd.to_datetime(data["date"])
    base = alt.Chart(data).encode(x=alt.X("date:T", title=None, axis=alt.Axis(format="%d %b")))
    line = base.mark_line(interpolate="monotone", color="#8E7BBF", strokeWidth=2.5).encode(
        y=alt.Y("mood:Q", scale=alt.Scale(domain=[-1, 1]), title="Mood (−1 low · +1 bright)"))
    points = base.mark_circle(size=55, color="#8E7BBF").encode(
        y="mood:Q", tooltip=[alt.Tooltip("date:T", format="%d %b"), alt.Tooltip("mood:Q", format=".2f"), "checkins"])
    zero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="#CFC6DE", strokeDash=[4, 4]).encode(y="y:Q")
    return style((zero + line + points).properties(height=220))


def calendar(days_table, days, now=None):
    """A calendar heatmap: weeks across, weekdays down, colour = average mood (grey = no check-in)."""
    today = (now or datetime.now()).date()
    start = today - timedelta(days=days - 1)
    moods = {d: m for d, m in zip(days_table["date"], days_table["mood"])}
    rows = []
    for i in range(days):
        day = start + timedelta(days=i)
        rows.append({"date": pd.Timestamp(day), "week": (day - (start - timedelta(days=start.weekday()))).days // 7,
                     "weekday": WEEKDAYS[day.weekday()], "mood": moods.get(day)})
    data = pd.DataFrame(rows)
    cell = 14 if days > 60 else 26
    chart = alt.Chart(data).mark_rect(cornerRadius=3, stroke="#FFFFFF", strokeWidth=1.5).encode(
        x=alt.X("week:O", title=None, axis=None), y=alt.Y("weekday:N", sort=WEEKDAYS, title=None),
        color=alt.condition("datum.mood === null", alt.value("#ECE7F2"),
                            alt.Color("mood:Q", title="Mood", scale=alt.Scale(domain=[-1, 0, 1],
                                                                              range=["#7F93BF", "#F1EDE6", "#CDAA78"]))),
        tooltip=[alt.Tooltip("date:T", format="%a %d %b"), alt.Tooltip("mood:Q", format=".2f")])
    return style(chart.properties(height=cell * 7, width=alt.Step(cell)))


# ---------------------------------------------------------------
# The page
# ---------------------------------------------------------------
def patterns_page():
    section_header("Patterns", "What your check-ins show",
                   "Patterns we noticed in your own check-ins. They describe, they don't diagnose: only you know "
                   "what was going on.", first=True)
    label = st.segmented_control("Period", list(RANGES), default="14 days", key="pattern_range",
                                 label_visibility="collapsed") or "14 days"
    days = RANGES[label]
    table = in_range(entries_table(), days)
    if not enough_data(table, days):
        have = table["date"].nunique() if not table.empty else 0
        with st.container(key="glass-pattern-empty"):
            st.html(f'<div class="title-sm">Not enough data yet</div><p class="body">Patterns over {esc(label)} need '
                    f"check-ins on at least {MIN_DAYS[days]} different days (so far: {have}). Keep checking in on the "
                    "Feel tab, or load the demo journal in My Galaxy to see how this page works.</p>")
        return
    if table["demo"].any():
        note("This period includes <b>demo entries</b>, so the patterns below are partly made up for presentations.")

    days_table = daily(table)
    kinds = days_table["kind"].value_counts()
    st.html('<div class="stats" style="margin-bottom:1rem">'
            f'<div class="stat"><b>{len(table)}</b>check-ins</div>'
            f'<div class="stat"><b>{len(days_table)}</b>days</div>'
            f'<div class="stat"><b>{kinds.get("bright", 0)}</b>bright days</div>'
            f'<div class="stat"><b>{kinds.get("in-between", 0)}</b>in-between days</div>'
            f'<div class="stat"><b>{kinds.get("low", 0)}</b>low days</div></div>')

    left, right = st.columns(2, gap="medium")
    with left:
        with st.container(key="glass-pattern-families"):
            st.html('<div class="eyebrow">How often each feeling appeared</div>')
            st.altair_chart(family_bars(table), width="stretch")
    with right:
        with st.container(key="glass-pattern-line"):
            st.html('<div class="eyebrow">Mood over time</div>')
            st.altair_chart(mood_line(days_table), width="stretch")
    with st.container(key="glass-pattern-calendar"):
        st.html('<div class="eyebrow">Calendar</div><p class="body" style="margin:.2rem 0 .5rem">Each square is a day: '
                "gold = brighter, blue = lower, grey = no check-in.</p>")
        st.altair_chart(calendar(days_table, days), width="content" if days > 60 else "stretch")

    weekdays, parts = low_clusters(table)
    with st.container(key="glass-pattern-noticed"):
        st.html('<div class="eyebrow">A pattern we noticed</div>')
        if weekdays:
            day, count = weekdays[0]
            part, part_count = parts[0]
            st.html(f'<p class="insight">Lower moods showed up most on <b>{esc(day)}</b> ({count} '
                    f"check-in{'s' if count != 1 else ''}) and most often in the <b>{esc(part.lower())}</b> "
                    f"({part_count}). Is there something about that time that could be a little easier?</p>")
        else:
            st.html('<p class="insight">No low-mood check-ins in this period.</p>')
        best = days_table.sort_values("mood").iloc[-1]
        st.html(f'<p class="insight">Your brightest day was <b>{best["date"].strftime("%a %d %b")}</b>.</p>')

    layer = low_pattern(days_table)
    if layer:
        with st.container(key="glass-pattern-support"):
            st.html('<div class="eyebrow">Some things that might help</div><p class="body">Low days have come up '
                    "quite often in this period. That happens to everyone sometimes. Here are some options, from "
                    "small to bigger:</p>")
            a, b, c = st.columns(3)
            a.button("1 · A calming tool", key="pat_calm", on_click=go_to, args=("Calm Room",), width="stretch")
            b.button("1 · A stress-buster game", key="pat_games", on_click=go_to, args=("Stress busters",),
                     width="stretch")
            c.button("2 · Tell someone (Reach Out)", key="pat_reach", on_click=go_to, args=("Reach Out",),
                     width="stretch")
            if layer >= 3:
                st.html('<p class="body" style="margin-top:.8rem"><b>3 ·</b> Because this has lasted about two weeks, '
                        "it could really help to talk to a trusted adult or a school counsellor. You can also call "
                        "<b>Tele-MANAS on 14416</b> (free, confidential, any time).</p>")
    note("These patterns use ORBIT's emotion model on your own words, so they can be wrong. The numbers that decide "
         "\"low\" or \"frequent\" are rules of thumb, not medical thresholds.")
