"""
ai_lab.py
The AI Lab: how ORBIT's AI works, how well it works, and whether it helps.

1. Pipeline      - the steps every message goes through
2. Evaluation    - accuracy on data/eval_set.csv (70 labelled sentences in
                   English, Hinglish and Hindi), a confusion matrix, and a
                   before/after test of the Hinglish translator
3. Impact study  - mood before vs after Calm Room sessions, plus feedback
4. Model card    - facts and limitations of the pre-trained model

This covers the Evaluation stage of the CBSE AI Project Cycle.
"""
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

import storage
from components import esc, note, section_header
from emotion_model import EMOTION_GROUPS, GROUP_OF, detect_emotions
from hinglish import to_english
from journal import style

EVAL_FILE = Path(__file__).parent / "data" / "eval_set.csv"
FAMILIES = list(EMOTION_GROUPS)


@st.cache_data(show_spinner=False, persist="disk")
def run_evaluation(file_changed):
    """Score every sentence twice: as typed, and after the Hinglish translator.

    file_changed is the file's modification time, so editing the CSV re-runs it.
    """
    table = pd.read_csv(EVAL_FILE)
    raw, translated, understood = [], [], []
    for text in table["text"]:
        raw.append(GROUP_OF[detect_emotions(text)[0][0]])
        english, _ = to_english(text)
        understood.append(english)
        translated.append(GROUP_OF[detect_emotions(english)[0][0]])
    table["predicted_raw"] = raw
    table["understood_as"] = understood
    table["predicted"] = translated
    return table


def per_family_report(table):
    rows = []
    for family in FAMILIES:
        tp = ((table["predicted"] == family) & (table["expected"] == family)).sum()
        predicted = (table["predicted"] == family).sum()
        actual = (table["expected"] == family).sum()
        precision = tp / predicted if predicted else 0.0
        recall = tp / actual if actual else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        rows.append({"Family": family, "Sentences": int(actual), "Precision": round(precision, 2),
                     "Recall": round(recall, 2), "F1": round(f1, 2)})
    return pd.DataFrame(rows)


def confusion_chart(table):
    counts = table.groupby(["expected", "predicted"], as_index=False).size()
    grid = pd.DataFrame([(e, p) for e in FAMILIES for p in FAMILIES], columns=["expected", "predicted"])
    grid = grid.merge(counts, how="left").fillna({"size": 0})
    base = alt.Chart(grid).encode(
        x=alt.X("predicted:N", sort=FAMILIES, title="ORBIT predicted"),
        y=alt.Y("expected:N", sort=FAMILIES, title="Correct answer"),
    )
    cells = base.mark_rect(cornerRadius=4).encode(
        color=alt.Color("size:Q", legend=None, scale=alt.Scale(range=["#F8F6F2", "#8E7BBF"])),
        tooltip=["expected", "predicted", alt.Tooltip("size:Q", title="sentences")],
    )
    labels = base.mark_text(fontSize=12).encode(
        text=alt.condition("datum.size > 0", alt.Text("size:Q", format=".0f"), alt.value("")),
        color=alt.condition("datum.size > 3", alt.value("#FFFFFF"), alt.value("#34313B")),
    )
    return style((cells + labels).properties(height=300))


def accuracy(series_a, series_b):
    return (series_a == series_b).mean() if len(series_a) else 0.0


def submit_feedback():
    storage.add_feedback(st.session_state.fb_rating, st.session_state.get("fb_comment", "").strip())
    st.session_state.fb_comment = ""
    st.session_state.flash.append("Thank you! Your feedback was saved for the impact study.")


def ai_lab_page():
    section_header(
        "AI Lab",
        "How ORBIT thinks",
        "A look inside the AI: the steps it follows, how accurate it is, and whether it actually helps people.",
        first=True,
    )

    # 1. Pipeline
    steps = [
        ("Check", "Is there real text with words?"),
        ("Translate", "Hinglish / Hindi words → English"),
        ("Detect", "RoBERTa model scores 28 emotions"),
        ("Explain", "Which words drove the result"),
        ("Protect", "Safety check for crisis words"),
        ("Respond", "Companion reply, world and coping tool"),
    ]
    st.html('<div class="pipeline">' + "".join(
        f'<div class="pipe-step"><span>{i:02d}</span><b>{esc(name)}</b><small>{esc(text)}</small></div>'
        for i, (name, text) in enumerate(steps, 1)) + "</div>")

    # 2. Evaluation
    st.html('<div class="section-head"><div class="eyebrow">Evaluation</div>'
            '<div class="title-sm" style="font-size:1.9rem">How accurate is the emotion model?</div>'
            '<p class="lede">ORBIT is tested on 70 sentences written the way Indian students talk, each labelled '
            "with the correct emotion family. A prediction counts as correct when the model's strongest emotion "
            "belongs to that family.</p></div>")
    with st.spinner("Testing the model on every sentence (about a minute the first time, instant after)…"):
        table = run_evaluation(EVAL_FILE.stat().st_mtime)
    english = table[table["language"] == "en"]
    other = table[table["language"] != "en"]
    raw_other = accuracy(other["predicted_raw"], other["expected"])
    new_other = accuracy(other["predicted"], other["expected"])
    st.html(
        '<div class="stats">'
        f'<div class="stat"><b>{accuracy(table["predicted"], table["expected"]):.0%}</b>overall accuracy</div>'
        f'<div class="stat"><b>{accuracy(english["predicted"], english["expected"]):.0%}</b>English ({len(english)})</div>'
        f'<div class="stat"><b>{raw_other:.0%} → {new_other:.0%}</b>Hinglish &amp; Hindi ({len(other)}), '
        "before → after translator</div></div>"
    )
    left, right = st.columns([1.3, 1], gap="medium")
    with left:
        with st.container(key="glass-confusion"):
            st.html('<div class="eyebrow">Confusion matrix</div><p class="body" style="margin:.2rem 0 .4rem">'
                    "The diagonal shows correct answers. Off-diagonal squares show which feelings get mixed up."
                    "</p>")
            st.altair_chart(confusion_chart(table), width="stretch")
    with right:
        with st.container(key="glass-report"):
            st.html('<div class="eyebrow">Per-family scores</div><p class="body" style="margin:.2rem 0 .6rem">'
                    "Precision: when ORBIT says a feeling, how often is it right? Recall: how many of that "
                    "feeling did it catch?</p>")
            st.dataframe(per_family_report(table), hide_index=True, width="stretch")

    wrong = table[table["predicted"] != table["expected"]]
    with st.expander(f"Sentences ORBIT got wrong ({len(wrong)})"):
        st.dataframe(wrong[["text", "language", "expected", "predicted", "understood_as"]],
                     hide_index=True, width="stretch")
    note("<b>Honest limitation:</b> the Hinglish translator's dictionary was written while looking at these "
         "Hinglish test sentences, so its score here is higher than it would be on new text. For a fair test, "
         "add fresh sentences from classmates (with permission) to <b>data/eval_set.csv</b>. The page updates "
         "automatically.")

    # 3. Impact study
    st.html('<div class="section-head"><div class="eyebrow">Impact study</div>'
            '<div class="title-sm" style="font-size:1.9rem">Does ORBIT actually help?</div>'
            '<p class="lede">Each Calm Room session records how the user felt before and after (1 = very low, '
            "5 = great). This is real evidence collected inside the app.</p></div>")
    sessions = pd.DataFrame(storage.list_wellbeing())
    if sessions.empty:
        note("No Calm Room sessions yet. Try an exercise in the Calm Room, or load the demo journal on the "
             "Journal page, to see results here.")
    else:
        sessions["change"] = sessions["after"] - sessions["before"]
        improved = (sessions["change"] > 0).mean()
        demo = " (includes demo data)" if sessions["demo"].any() else ""
        st.html(
            '<div class="stats">'
            f'<div class="stat"><b>{len(sessions)}</b>sessions{demo}</div>'
            f'<div class="stat"><b>{sessions["before"].mean():.1f} → {sessions["after"].mean():.1f}</b>average mood</div>'
            f'<div class="stat"><b>{improved:.0%}</b>felt better afterwards</div></div>'
        )
        by_tool = sessions.groupby("tool", as_index=False)[["before", "after"]].mean().melt(
            id_vars="tool", var_name="when", value_name="mood")
        chart = alt.Chart(by_tool).mark_bar(cornerRadius=5).encode(
            x=alt.X("tool:N", title=None), xOffset="when:N",
            y=alt.Y("mood:Q", title="Average mood (1–5)", scale=alt.Scale(domain=[0, 5])),
            color=alt.Color("when:N", title=None, scale=alt.Scale(domain=["before", "after"],
                                                                  range=["#B9C8EA", "#8E7BBF"])),
            tooltip=["tool", "when", alt.Tooltip("mood:Q", format=".1f")],
        )
        with st.container(key="glass-impact"):
            st.altair_chart(style(chart.properties(height=240)), width="stretch")

    with st.container(key="glass-feedback"):
        st.html('<div class="eyebrow">Feedback</div>')
        st.select_slider("How helpful was ORBIT today?", options=[1, 2, 3, 4, 5], value=4, key="fb_rating",
                         format_func={1: "Not at all", 2: "A little", 3: "Somewhat", 4: "Helpful",
                                      5: "Very helpful"}.get)
        st.text_input("Anything you'd like to tell the creator? (optional)", key="fb_comment")
        st.button("Send feedback", key="fb_send", on_click=submit_feedback)
        feedback = storage.list_feedback()
        if feedback:
            average = sum(f["rating"] for f in feedback) / len(feedback)
            st.html(f'<p class="body">{len(feedback)} response{"s" if len(feedback) != 1 else ""} · '
                    f"average {average:.1f} / 5</p>")

    # 4. Model card
    st.html(
        '<div class="section-head"><div class="eyebrow">Model card</div>'
        '<div class="title-sm" style="font-size:1.9rem">About the model</div></div>'
        '<div class="model-card">'
        "<div><span>Model</span>SamLowe/roberta-base-go_emotions-onnx (quantized, ~125 MB, MIT licence)</div>"
        "<div><span>Type</span>RoBERTa transformer, multi-label: 28 independent emotion scores</div>"
        "<div><span>Trained on</span>Google GoEmotions: ~58,000 English Reddit comments labelled by people</div>"
        "<div><span>Runs</span>Offline on the laptop's CPU with ONNX Runtime; no data leaves the device</div>"
        "<div><span>Limitations</span>English-first; Hinglish/Hindi via a simple word translator; can misread "
        "sarcasm, very short texts and feelings described only through the body</div>"
        "<div><span>Not for</span>Diagnosis. ORBIT supports wellbeing; it does not replace professionals</div>"
        "</div>"
    )
