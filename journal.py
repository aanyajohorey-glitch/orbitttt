"""
journal.py
The private mood journal: charts, insights and a galaxy of emotion planets.

Every check-in (Home, Mood Lab, Companion) is saved on this computer in
data/orbit.db (see storage.py). This page turns those entries into:
- an "emotional weather" line (mood score from -1 to +1 per day)
- the mix of emotion families each day
- patterns by weekday and written insights
- a galaxy: one planet per check-in, coloured by emotion, sized by intensity,
  with a ring when two different feelings were mixed together
"""
import json
import random
from datetime import datetime, timedelta

import altair as alt
import pandas as pd
import streamlit as st

import storage
from components import esc, note, planet_html, section_header
from constellation import constellation_planet
from analysis import interpret
from emotion_model import GROUP_COLOURS, GROUP_OF, mood_score

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


# ---------------------------------------------------------------
# Demo data for presentations (clearly marked, easy to remove)
# ---------------------------------------------------------------
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
DEMO_SESSIONS = [("Breathing", 2, 4), ("Grounding", 2, 3), ("Thought Reframe", 1, 3), ("Breathing", 3, 4),
                 ("Gratitude Jar", 3, 5), ("Breathing", 2, 3)]


def load_demo():
    rng = random.Random(14)
    start = datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(days=len(DEMO_STORY) - 1)
    for day, text in enumerate(DEMO_STORY):
        when = (start + timedelta(days=day)).replace(hour=rng.randint(17, 22))
        result = interpret(text)   # the same pipeline as a real check-in
        storage.add_entry("Demo", text, result["emotions"], result["world"], primary=result["final"]["emotion"],
                          created_at=when.isoformat(timespec="seconds"), demo=True)
    for i, (tool, before, after) in enumerate(DEMO_SESSIONS):
        when = start + timedelta(days=i * 2 + 1, hours=20)
        storage.add_wellbeing(tool, before, after, created_at=when.isoformat(timespec="seconds"), demo=True)
    written = (datetime.now() - timedelta(days=31)).isoformat(timespec="seconds")
    storage.add_note("future_letter", (datetime.now() - timedelta(days=1)).date().isoformat(),
                     json.dumps({"letter": "Hi future me. Pre-boards are next week and I'm scared about maths. "
                                 "I hope you're proud that you kept going, whatever the marks were.",
                                 "feeling": "Worried", "demo": True}), created_at=written)
    st.session_state.flash.append("Loaded a 14-day demo journal (marked as demo).")


def clear_demo():
    for item in storage.list_notes("future_letter"):
        if '"demo": true' in item["text"]:
            storage.delete_note(item["id"])
    storage.clear_entries(demo_only=True)
    storage.clear_wellbeing(demo_only=True)
    st.session_state.flash.append("Demo data removed.")


def delete_entry(entry_id):
    storage.delete_entry(entry_id)
    st.session_state.flash.append("Entry deleted.")


# ---------------------------------------------------------------
# Charts (Altair, styled to match ORBIT)
# ---------------------------------------------------------------
def style(chart):
    return (chart.configure(background="transparent", font=FONT)
            .configure_view(strokeWidth=0)
            .configure_axis(labelColor="#6B6773", titleColor="#6B6773", gridColor="#ECE7F2",
                            domainColor="#DDD6E8", tickColor="#DDD6E8", labelFontSize=11, titleFontSize=11)
            .configure_legend(labelColor="#4A4553", titleColor="#6B6773", orient="bottom"))


def weather_chart(table):
    daily = table.groupby("date", as_index=False)["mood"].mean()
    daily["date"] = pd.to_datetime(daily["date"])
    base = alt.Chart(daily).encode(x=alt.X("date:T", title=None, axis=alt.Axis(format="%d %b")))
    area = base.mark_area(
        interpolate="monotone", opacity=0.35,
        color=alt.Gradient(gradient="linear", x1=1, x2=1, y1=1, y2=0,
                           stops=[alt.GradientStop(color="#B9C8EA", offset=0),
                                  alt.GradientStop(color="#C9B9E8", offset=1)]),
    ).encode(y=alt.Y("mood:Q", scale=alt.Scale(domain=[-1, 1]), title="Mood (−1 low · +1 bright)"))
    line = base.mark_line(interpolate="monotone", color="#8E7BBF", strokeWidth=2.5).encode(y="mood:Q")
    points = base.mark_circle(size=60, color="#8E7BBF").encode(
        y="mood:Q", tooltip=[alt.Tooltip("date:T", format="%d %b"), alt.Tooltip("mood:Q", format=".2f")])
    zero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="#CFC6DE", strokeDash=[4, 4]).encode(y="y:Q")
    return style((area + zero + line + points).properties(height=240))


def family_chart(table):
    counts = table.groupby(["date", "family"], as_index=False).size()
    counts["day"] = pd.to_datetime(counts["date"]).dt.strftime("%d %b")
    order = list(dict.fromkeys(counts.sort_values("date")["day"]))
    families = list(GROUP_COLOURS)
    chart = alt.Chart(counts).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X("day:O", sort=order, title=None, axis=alt.Axis(labelAngle=-45)),
        y=alt.Y("size:Q", title="Check-ins", axis=alt.Axis(tickMinStep=1)),
        color=alt.Color("family:N", title=None, legend=alt.Legend(orient="bottom", columns=4), scale=alt.Scale(
            domain=families, range=[GROUP_COLOURS[f][1] for f in families])),
        tooltip=["family", "size"],
    )
    return style(chart.properties(height=220))


def weekday_chart(table):
    by_day = table.groupby("weekday", as_index=False)["mood"].mean()
    chart = alt.Chart(by_day).mark_bar(cornerRadius=6, color="#C9B9E8").encode(
        x=alt.X("weekday:N", sort=WEEKDAYS, title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("mood:Q", title="Average mood", scale=alt.Scale(domain=[-1, 1])),
        tooltip=["weekday", alt.Tooltip("mood:Q", format=".2f")],
    )
    return style(chart.properties(height=200))


# ---------------------------------------------------------------
# Insights written from the data
# ---------------------------------------------------------------
def insights(table, sessions):
    lines = []
    top = table["family"].value_counts()
    lines.append(f"Your most common feeling family is <b>{top.index[0]}</b> "
                 f"({top.iloc[0] / len(table):.0%} of check-ins).")
    by_day = table.groupby("weekday")["mood"].mean()
    if len(by_day) >= 3:
        lines.append(f"<b>{by_day.idxmax()}</b> tends to be your brightest day and "
                     f"<b>{by_day.idxmin()}</b> your toughest.")
    recent = table[table["when"] >= datetime.now() - timedelta(days=7)]["mood"]
    earlier = table[(table["when"] < datetime.now() - timedelta(days=7)) &
                    (table["when"] >= datetime.now() - timedelta(days=14))]["mood"]
    if len(recent) and len(earlier):
        change = recent.mean() - earlier.mean()
        direction = "brighter" if change > 0.05 else "lower" if change < -0.05 else "about the same"
        lines.append(f"This week your mood has been <b>{direction}</b> than the week before ({change:+.2f}).")
    if sessions:
        gains = pd.DataFrame(sessions)
        gains["change"] = gains["after"] - gains["before"]
        best = gains.groupby("tool")["change"].mean()
        lines.append(f"Calm Room sessions lifted your mood by <b>{gains['change'].mean():+.1f}</b> points on average; "
                     f"<b>{best.idxmax()}</b> helped most.")
    days = sorted(set(table["date"]), reverse=True)
    streak, expected = 0, datetime.now().date()
    for day in days:
        if day == expected or (streak == 0 and day == expected - timedelta(days=1)):
            streak += 1
            expected = day - timedelta(days=1)
        else:
            break
    if streak >= 2:
        lines.append(f"You're on a <b>{streak}-day</b> check-in streak. That's real self-care.")
    return lines


def entry_planet(emotions, primary=None, size=None):
    primary = primary or emotions[0][0]
    score = dict(emotions).get(primary, emotions[0][1])
    light, dark = GROUP_COLOURS[GROUP_OF[primary]]
    mixed = any(s >= 0.12 and GROUP_OF[l] != GROUP_OF[primary] and l != "neutral" for l, s in emotions[:4] if l != primary)
    return planet_html(light, dark, size or int(34 + 46 * score), ring=mixed, delay=random.random() * 6)


def galaxy_html(table):
    stars = []
    for _, row in table.tail(42).iterrows():
        size = int(48 + 40 * row["score"])
        planet = constellation_planet(row["emotions"], row["primary"], row["text"], size=size, uid=f"g{row['id']}")
        stars.append(
            f'<div class="galaxy-star" title="{esc(row["when"].strftime("%d %b"))} · {esc(row["primary"])}">'
            f'{planet}'
            f'<small>{row["when"].strftime("%d %b")}</small></div>'
        )
    return f'<div class="galaxy">{"".join(stars)}</div>'


# ---------------------------------------------------------------
# The page
# ---------------------------------------------------------------
def journal_page():
    section_header(
        "Journal",
        "Your emotional weather",
        "Every check-in becomes a planet in your personal galaxy. Over time, patterns appear: what lifts you, "
        "what weighs on you, and what helps.",
        first=True,
    )
    if not storage.journal_enabled():
        note("Journaling is switched off, so new check-ins aren't saved. You can turn it on in the Care page.")

    table = entries_table()
    sessions = storage.list_wellbeing()
    has_demo = not table.empty and table["demo"].any()

    if table.empty:
        st.html('<div class="empty">' + planet_html("#EFEAF7", "#C9B9E8", 70, ring=True)
                + '<div class="title-sm">Your galaxy is waiting</div><p class="body">Check in on Home, in the '
                "Mood Lab or with the Companion, and your planets will appear here.</p></div>")
        _, mid, _ = st.columns([1, 1.2, 1])
        mid.button("Load a 14-day demo journal", key="demo_load", on_click=load_demo, width="stretch")
        return

    if has_demo:
        note("This journal includes <b>demo entries</b> for presentations. Remove them any time.")

    days = table["date"].nunique()
    st.html(
        '<div class="stats" style="margin-bottom:1rem">'
        f'<div class="stat"><b>{len(table)}</b>check-ins</div>'
        f'<div class="stat"><b>{days}</b>days</div>'
        f'<div class="stat"><b>{table["family"].mode()[0]}</b>most common</div>'
        f'<div class="stat"><b>{table["mood"].mean():+.2f}</b>average mood</div>'
        f'<div class="stat"><b>{len(sessions)}</b>calm sessions</div></div>'
    )

    with st.container(key="glass-galaxy"):
        st.html('<div class="eyebrow">Your galaxy</div><p class="body" style="margin:.2rem 0 .6rem">'
                "Colour = main feeling · size = how strong · the stars on each planet are that day's emotion constellation</p>" + galaxy_html(table))
        legend = "".join(f'<span class="legend-dot" style="--c:{GROUP_COLOURS[f][1]}"></span>{f}'
                         for f in GROUP_COLOURS)
        st.html(f'<div class="legend">{legend}</div>')

    with st.container(key="glass-insights"):
        st.html('<div class="eyebrow">Insights</div>'
                + "".join(f'<p class="insight">{line}</p>' for line in insights(table, sessions)))

    left, right = st.columns(2, gap="medium")
    with left:
        with st.container(key="glass-weather"):
            st.html('<div class="eyebrow">Emotional weather</div>')
            st.altair_chart(weather_chart(table), width="stretch")
    with right:
        with st.container(key="glass-mix"):
            st.html('<div class="eyebrow">Feeling families by day</div>')
            st.altair_chart(family_chart(table), width="stretch")
    with st.container(key="glass-weekday"):
        st.html('<div class="eyebrow">By day of the week</div>')
        st.altair_chart(weekday_chart(table), width="stretch")

    with st.expander(f"All entries ({len(table)})"):
        for _, row in table.iloc[::-1].iterrows():
            info, action = st.columns([6, 1], vertical_alignment="center")
            info.html(
                f'<div class="entry-row"><span class="eyebrow">{row["when"].strftime("%d %b %Y, %H:%M")} · '
                f'{esc(row["source"])} · {esc(row["primary"])} {row["score"]:.0%} → {esc(row["world"])}</span>'
                f'<p class="body">{esc(row["text"])}</p></div>'
            )
            action.button("Delete", key=f"del_entry_{row['id']}", type="tertiary", on_click=delete_entry,
                          args=(int(row["id"]),))

    export = table.drop(columns=["emotions", "id", "demo"]).to_csv(index=False).encode("utf-8")
    left, right, _ = st.columns([1.2, 1.2, 2])
    left.download_button("Download journal (CSV)", export, file_name="orbit_journal.csv", mime="text/csv",
                         width="stretch")
    if has_demo:
        right.button("Remove demo data", key="demo_clear", on_click=clear_demo, width="stretch")
    else:
        right.button("Add demo data", key="demo_load2", on_click=load_demo, width="stretch")
