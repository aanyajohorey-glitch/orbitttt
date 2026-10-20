"""
ai_lab.py
The AI Lab: how ORBIT's AI works, how well it works, where it fails, and
whether it helps. This page is the Evaluation stage of the CBSE AI Project
Cycle. Every number on it is computed live from the files in data/.

Sections
  1. Pipeline                 6. Confidence (when ORBIT should ask)
  2. Datasets                 7. Safety test suite
  3. Model comparison         8. Teach Orbit (human-in-the-loop learning)
  4. Body-described feelings  9. Fairness and bias
  5. Hinglish: classifier vs dictionary   10. Impact study   11. Model card
"""
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

import datasets
import evaluation
import orbit_head
import safety
import storage
import train_head
from analysis import UNSURE_BELOW, current_head
from components import esc, note, section_header
from journal import style

FAMILIES = orbit_head.FAMILIES
DATASET_INFO = {
    "dev": ("Development set (70)", "Author-written. Hinglish/Hindi results are OPTIMISTIC for the dictionary, "
                                    "which was written while looking at these sentences."),
    "body": ("Body-feelings set (33)", "Author-written focused test: 20 anxious sentences described through the "
                                       "body + 13 body sentences that are NOT anxiety (controls)."),
    "heldout": ("Held-out set (classmates)", "The fair test. Never used for training or tuning."),
}


# ---------------------------------------------------------------
# Cached computations
# ---------------------------------------------------------------
@st.cache_data(show_spinner=False)
def predictions(name, version, model_version):
    table = datasets.load(name)
    return evaluation.predict(table, private=(name == "heldout"))


@st.cache_data(show_spinner=False)
def out_of_fold(train_version, model_version):
    """Out-of-fold predictions on the TRAINING data: each sentence is predicted by
    a model that never saw it (5-fold cross-validation)."""
    table = datasets.load("train")
    for variant in ("C", "D"):
        _, _, meta = orbit_head.load(orbit_head.CANDIDATES[variant])
        probs = train_head.out_of_fold(variant == "D", meta["l2"], meta.get("temperature", 1.0))
        table[f"pred_{variant}"] = [FAMILIES[i] for i in probs.argmax(axis=1)]
        if variant == adopted_variant():
            table["confidence"] = probs.max(axis=1)
    table["pred_B"] = evaluation.predict(table[["text", "language", "family", "style"]])["pred_B"]
    table["pred_live"] = table[f"pred_{adopted_variant()}"]
    return table


def adopted_variant():
    """Which candidate (C or D) is the live model."""
    _, _, meta = orbit_head.load(orbit_head.SHARED_MODEL)
    return "D" if meta.get("uses_dictionary") else "C"


@st.cache_data(show_spinner=False)
def safety_results(version):
    table = pd.read_csv(datasets.DATA / "safety_tests.csv", encoding="utf-8")
    table["detected"] = [safety.check(t) or "none" for t in table["text"]]
    return table


def model_version():
    path = orbit_head.SHARED_MODEL
    return path.stat().st_mtime if path.exists() else 0


def file_mtime(path):
    return path.stat().st_mtime if path.exists() else 0


# ---------------------------------------------------------------
# Small drawing helpers
# ---------------------------------------------------------------
def stats_html(items):
    return '<div class="stats">' + "".join(
        f'<div class="stat"><b>{esc(value)}</b>{esc(label)}</div>' for value, label in items) + "</div>"


def heading(eyebrow, title, text=""):
    st.html(f'<div class="section-head"><div class="eyebrow">{eyebrow}</div>'
            f'<div class="title-sm" style="font-size:1.9rem">{title}</div>'
            + (f'<p class="lede">{text}</p>' if text else "") + "</div>")


def confusion_chart(y_true, y_pred):
    grid = evaluation.confusion(y_true, y_pred).reset_index().melt(id_vars="Correct", var_name="Predicted",
                                                                    value_name="n")
    base = alt.Chart(grid).encode(x=alt.X("Predicted:N", sort=FAMILIES, title="ORBIT predicted"),
                                  y=alt.Y("Correct:N", sort=FAMILIES, title="Correct answer"))
    cells = base.mark_rect(cornerRadius=4).encode(
        color=alt.Color("n:Q", legend=None, scale=alt.Scale(range=["#F8F6F2", "#8E7BBF"])),
        tooltip=["Correct", "Predicted", "n"])
    labels = base.mark_text(fontSize=12).encode(
        text=alt.condition("datum.n > 0", alt.Text("n:Q"), alt.value("")),
        color=alt.condition("datum.n > 3", alt.value("#FFFFFF"), alt.value("#34313B")))
    return style((cells + labels).properties(height=290))


def comparison_table(table):
    rows = []
    for v, label in evaluation.VARIANTS.items():
        r = evaluation.report(table["family"], table[f"pred_{v}"])
        rows.append({"Method": f"{v} · {label}" + ("  (live)" if v == adopted_variant() else ""),
                     "Accuracy": round(r["accuracy"], 2), "Macro-F1": round(r["macro_f1"], 3)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------
# Teach Orbit retraining
# ---------------------------------------------------------------
def retrain_with_corrections():
    corrections = storage.list_corrections()
    extra = [(c["text"], c["corrected"], c["raw_scores"]["raw"], c["raw_scores"]["dict"]) for c in corrections]
    _, _, shared_meta = orbit_head.load(orbit_head.SHARED_MODEL)
    X, y, w = train_head.training_arrays(extra, shared_meta.get("uses_dictionary", False))
    W, b = orbit_head.train(X, y, w, l2=shared_meta["l2"])
    meta = dict(shared_meta, corrections=len(extra), train_sentences=int(len(y)))
    orbit_head.save(orbit_head.PERSONAL_MODEL, W, b, meta)
    st.session_state.flash.append(f"ORBIT retrained with your {len(extra)} correction(s). "
                                  "This personal model stays on this computer.")


def reset_personal_model():
    if orbit_head.PERSONAL_MODEL.exists():
        orbit_head.PERSONAL_MODEL.unlink()
    st.session_state.flash.append("Back to ORBIT's shared model.")


def before_after(name):
    table = datasets.load(name)
    if table.empty or not orbit_head.PERSONAL_MODEL.exists():
        return None
    before = evaluation.predict(table, orbit_head.load(orbit_head.SHARED_MODEL), private=(name == "heldout"))
    after = evaluation.predict(table, orbit_head.load(orbit_head.PERSONAL_MODEL), private=(name == "heldout"))
    b = evaluation.report(before["family"], before["pred_live"])
    a = evaluation.report(after["family"], after["pred_live"])
    return {"Test set": DATASET_INFO[name][0], "Macro-F1 before": round(b["macro_f1"], 3),
            "Macro-F1 after": round(a["macro_f1"], 3), "Change": round(a["macro_f1"] - b["macro_f1"], 3)}


def submit_feedback():
    storage.add_feedback(st.session_state.fb_rating, st.session_state.get("fb_comment", "").strip())
    st.session_state.fb_comment = ""
    st.session_state.flash.append("Thank you! Your feedback was saved on this computer.")


# ---------------------------------------------------------------
# The page
# ---------------------------------------------------------------
def ai_lab_page():
    section_header(
        "AI Lab",
        "How ORBIT thinks, and how we know",
        "The data, the models, the metrics and the mistakes. Every number here is calculated live from the "
        "files in data/, so it updates when new test sentences are added.",
        first=True,
    )
    if current_head() is None:
        note("ORBIT's trained classifier file is missing. Run <b>python train_head.py</b> to create it.")
        return
    mv = model_version()

    # 1. Pipeline -------------------------------------------------------------
    steps = [("Check", "Is there real text with words?"),
             ("Detect", "RoBERTa scores 28 emotions"),
             ("Decide", "ORBIT's trained classifier picks the family + confidence"),
             ("Ask", "If unsure, a gentle clarifying question"),
             ("Protect", "Deterministic crisis check, never AI"),
             ("Respond", "Companion reply, world, coping tool")]
    st.html('<div class="pipeline">' + "".join(
        f'<div class="pipe-step"><span>{i:02d}</span><b>{esc(n)}</b><small>{esc(t)}</small></div>'
        for i, (n, t) in enumerate(steps, 1)) + "</div>")

    # 2. Datasets ---------------------------------------------------------------
    heading("Data", "Where the numbers come from",
            "Training and testing use separate sentences. No test sentence is copied or closely "
            "paraphrased in the training data (checked automatically).")
    rows = [("train_augment.csv", len(datasets.load("train")), "Training", "Author-written"),
            ("eval_set.csv", len(datasets.load("dev")), "Development test", "Author-written"),
            ("eval_body.csv", len(datasets.load("body")), "Focused test (body feelings)", "Author-written"),
            ("eval_heldout.csv", len(datasets.load("heldout")), "Fair test (never tuned on)",
             "Classmates, anonymous, with teacher permission"),
            ("safety_tests.csv", len(safety_results(file_mtime(datasets.DATA / "safety_tests.csv"))),
             "Safety rules", "Author-written"),
            ("Teach Orbit corrections", len(storage.list_corrections()), "Optional extra training",
             "You (stored only on this computer)")]
    st.dataframe(pd.DataFrame(rows, columns=["Data", "Sentences", "Role", "Source"]), hide_index=True,
                 width="stretch")
    heldout_n = len(datasets.load("heldout"))
    if heldout_n == 0:
        note("<b>The held-out set is still empty.</b> Collect 150 to 200 anonymous sentences from classmates "
             "(with teacher permission), following <b>docs/data_collection_guide.md</b>, and save them as "
             "<b>data/eval_heldout.csv</b>. Until then, every test below is author-written, so treat the scores "
             "as a first check, not a final result.")

    # 3. Model comparison -------------------------------------------------------
    heading("Evaluation", "Three ways to read a feeling",
            "A = the pre-trained model alone · B = ORBIT v0.3 (model + hand-written Hinglish dictionary) · "
            "C = ORBIT's trained classifier · D = classifier that also sees the dictionary translation "
            "(“translation-assist”). Each was adopted only if it met a rule written BEFORE training "
            "(docs/methodology.md).")
    available = [n for n in ("heldout", "body", "dev") if not datasets.load(n).empty]
    choice = st.pills("Test set", available, format_func=lambda n: DATASET_INFO[n][0], key="lab_set",
                      default=available[0]) or available[0]
    table = predictions(choice, datasets.file_version(choice), mv)
    st.html(f'<p class="body" style="margin:.2rem 0 .8rem">{esc(DATASET_INFO[choice][1])}</p>')
    st.dataframe(comparison_table(table), hide_index=True, width="stretch")

    live = adopted_variant()
    variant = st.pills("Inspect method", list(evaluation.VARIANTS), default=live, key="lab_variant",
                       format_func=lambda v: f"{v} · {evaluation.VARIANTS[v]}") or live
    rep = evaluation.report(table["family"], table[f"pred_{variant}"])
    left, right = st.columns([1.25, 1], gap="medium")
    with left:
        with st.container(key="glass-confusion"):
            st.html('<div class="eyebrow">Confusion matrix</div><p class="body" style="margin:.2rem 0 .4rem">'
                    "The diagonal shows correct answers; other squares show which feelings get mixed up.</p>")
            st.altair_chart(confusion_chart(table["family"], table[f"pred_{variant}"]), width="stretch")
    with right:
        with st.container(key="glass-report"):
            st.html('<div class="eyebrow">Per-family precision, recall and F1</div>'
                    '<p class="body" style="margin:.2rem 0 .6rem">Precision: when ORBIT says a feeling, how '
                    "often is it right? Recall: how many of that feeling did it find? F1 balances both.</p>")
            st.dataframe(rep["per_family"], hide_index=True, width="stretch")
            st.html(stats_html([(f'{rep["accuracy"]:.0%}', "accuracy"), (f'{rep["macro_f1"]:.2f}', "macro-F1")]))
    left, right = st.columns(2, gap="medium")
    left.html('<div class="field-label">By language</div>')
    left.dataframe(evaluation.by_group(table, "language", variant), hide_index=True, width="stretch")
    right.html('<div class="field-label">By writing style</div>')
    right.dataframe(evaluation.by_group(table, "style", variant), hide_index=True, width="stretch")
    wrong = table[table["family"] != table[f"pred_{variant}"]]
    with st.expander(f"Sentences this method got wrong ({len(wrong)})"):
        st.dataframe(wrong[["text", "language", "style", "family", f"pred_{variant}"]].rename(
            columns={"family": "correct", f"pred_{variant}": "predicted"}), hide_index=True, width="stretch")

    # 4. Body-described feelings -----------------------------------------------
    heading("Fixing a known failure", "Feelings described through the body",
            "The pre-trained model read “my heart is racing before the presentation” as joy: it learned "
            "“racing heart” mostly from excited posts. ORBIT's classifier was trained with body-described "
            "anxiety AND body sentences that are not anxiety, so it can't just learn “body word = fear”.")
    body = predictions("body", datasets.file_version("body"), mv)
    fear_b = evaluation.family_f1(body["family"], body["pred_B"], "Fear")
    fear_live = evaluation.family_f1(body["family"], body["pred_live"], "Fear")
    controls = body[body["family"] != "Fear"]
    st.html(stats_html([
        (f"{fear_b:.2f} → {fear_live:.2f}", f"Fear F1 on body sentences (B → {live})"),
        (f'{(controls["pred_B"] == controls["family"]).mean():.0%} → '
         f'{(controls["pred_live"] == controls["family"]).mean():.0%}',
         f"non-anxiety controls read correctly (B → {live})"),
    ]))
    note("<b>Trade-off found:</b> the classifier now catches body-described anxiety much better, but it also "
         "reads some harmless body sentences as fear (for example “my hands are cold, I forgot my gloves”). "
         "The adoption rule didn't check controls, which was an oversight. Fixing it needs more non-anxiety "
         "training examples AND a new test set, since this one has now been looked at.")

    # 5. Hinglish ---------------------------------------------------------------
    heading("Hinglish and Hindi", "Trained classifier vs hand-written dictionary")
    oof = out_of_fold(datasets.file_version("train"), mv)
    non_en = oof[oof["language"] != "English"]
    rows = [{"Test": "Training Hinglish/Hindi, out-of-fold (fair: the dictionary never saw these)",
             "Sentences": len(non_en),
             "B · dictionary": round(evaluation.report(non_en["family"], non_en["pred_B"])["macro_f1"], 3),
             "C · classifier": round(evaluation.report(non_en["family"], non_en["pred_C"])["macro_f1"], 3),
             "D · classifier + dictionary": round(evaluation.report(non_en["family"], non_en["pred_D"])["macro_f1"], 3)}]
    dev = predictions("dev", datasets.file_version("dev"), mv)
    dev_non_en = dev[dev["language"] != "English"]
    rows.append({"Test": "Development set Hinglish/Hindi (optimistic for the dictionary)",
                 "Sentences": len(dev_non_en),
                 "B · dictionary": round(evaluation.report(dev_non_en["family"], dev_non_en["pred_B"])["macro_f1"], 3),
                 "C · classifier": round(evaluation.report(dev_non_en["family"], dev_non_en["pred_C"])["macro_f1"], 3),
                 "D · classifier + dictionary": round(evaluation.report(dev_non_en["family"], dev_non_en["pred_D"])["macro_f1"], 3)})
    if heldout_n:
        ho = predictions("heldout", datasets.file_version("heldout"), mv)
        ho_non_en = ho[ho["language"] != "English"]
        if len(ho_non_en):
            rows.append({"Test": "Held-out Hinglish/Hindi (the fair test)", "Sentences": len(ho_non_en),
                         "B · dictionary": round(evaluation.report(ho_non_en["family"], ho_non_en["pred_B"])["macro_f1"], 3),
                         "C · classifier": round(evaluation.report(ho_non_en["family"], ho_non_en["pred_C"])["macro_f1"], 3),
                         "D · classifier + dictionary": round(evaluation.report(ho_non_en["family"], ho_non_en["pred_D"])["macro_f1"], 3)})
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    note("Macro-F1 shown. <b>Finding:</b> on the fair test, the classifier ALONE (C) was worse than the "
         "hand-written dictionary (B): about 95 Hinglish training sentences per fold were not enough. Giving "
         "the classifier the dictionary's translation as extra evidence (D) beat both, so D is live. "
         "D's development-set score is optimistic, because the dictionary was written while looking at it.")

    # 6. Confidence -------------------------------------------------------------
    heading("Confidence", "Knowing when to ask",
            f"If the classifier's top probability is below {UNSURE_BELOW:.0%}, ORBIT asks a gentle question "
            "instead of naming a feeling. The threshold was chosen using out-of-fold predictions on the "
            "training data (each sentence judged by a model that never saw it).")
    bins = [0, 0.5, 0.7, 0.8, 1.01]
    oof["band"] = pd.cut(oof["confidence"], bins, right=False,
                         labels=["below 50%", "50-70%", "70-80%", "80% or more"])
    calib = oof.groupby("band", observed=False).apply(
        lambda g: pd.Series({"Sentences": int(len(g)), "Accuracy": round((g["pred_live"] == g["family"]).mean(), 2)
                             if len(g) else np.nan}), include_groups=False).reset_index()
    calib["Sentences"] = calib["Sentences"].astype(int)
    sure = oof["confidence"] >= UNSURE_BELOW
    st.dataframe(calib.rename(columns={"band": "Confidence"}), hide_index=True, width="stretch")
    st.html(stats_html([(f"{sure.mean():.0%}", "messages ORBIT is confident about"),
                        (f'{(oof[sure]["pred_live"] == oof[sure]["family"]).mean():.0%}', "accuracy when confident"),
                        (f'{(oof[~sure]["pred_live"] == oof[~sure]["family"]).mean():.0%}',
                         "accuracy when unsure (why it asks)")]))

    # 7. Safety -----------------------------------------------------------------
    heading("Safety", "Testing the crisis safety net",
            "The crisis check is deterministic (fixed rules, never AI). It is tested on direct and indirect "
            "phrasing in English, Hinglish and Hindi, plus 'trap' sentences such as “this homework is killing me”.")
    sr = safety_results(file_mtime(datasets.DATA / "safety_tests.csv"))
    crisis = sr[sr["expected"] == "crisis"]
    harmless = sr[sr["expected"] == "none"]
    st.html(stats_html([
        (f'{(crisis["detected"] == "crisis").mean():.0%}', f"crisis recall ({len(crisis)} crisis sentences)"),
        (f'{(harmless["detected"] != "none").mean():.0%}', f"false-alarm rate ({len(harmless)} harmless)"),
    ]))
    by_lang = sr[sr["expected"] == "crisis"].groupby("language").apply(
        lambda g: f'{(g["detected"] == "crisis").sum()}/{len(g)}', include_groups=False)
    st.html('<p class="body">Crisis recall by language: ' + " · ".join(f"{esc(k)} {v}" for k, v in by_lang.items())
            + "</p>")
    history = pd.DataFrame([
        ("0 (v0.3)", "direct phrases only", "0%"),
        ("1", "warning-sign patterns", "17%"),
        ("2", "methods, finality, idioms", "33%"),
        ("3", "fixes for reviewed misses", "needs a fresh holdout"),
    ], columns=["Round", "Change", "Recall on a NEW holdout"])
    st.dataframe(history, hide_index=True, width="stretch")
    misses = sr[(sr["expected"] == "crisis") & (sr["detected"] != "crisis")]
    note("<b>Important:</b> rules reach almost 100% on the sentences they were written from, but only "
         "17–33% on new wording. No rule list can foresee every way a person might say this, which is why "
         "helplines are always on the Care page and the companion always points to real people. "
         + (f"Known misses: {'; '.join(esc(t) for t in misses['text'])}. " if len(misses) else "")
         + "Full history: <b>docs/safety_report.md</b>.")

    # 8. Teach Orbit ------------------------------------------------------------
    heading("Human in the loop", "Teach Orbit",
            "When ORBIT is wrong, users can say so. Corrections are stored only on this computer and can be "
            "used to retrain the classifier. This is the same idea as how many real AI systems improve.")
    corrections = storage.list_corrections()
    personal = orbit_head.PERSONAL_MODEL.exists()
    st.html(stats_html([(str(len(corrections)), "corrections saved"),
                        ("personal" if personal else "shared", "model in use")]))
    if corrections:
        with st.expander(f"Your corrections ({len(corrections)})"):
            st.dataframe(pd.DataFrame(corrections)[["created_at", "text", "predicted", "corrected", "source"]],
                         hide_index=True, width="stretch")
    left, right, _ = st.columns([1.4, 1.2, 2])
    left.button("Retrain ORBIT with my corrections", key="lab_retrain", type="primary",
                disabled=not corrections, on_click=retrain_with_corrections, width="stretch")
    right.button("Use the shared model", key="lab_reset", disabled=not personal, on_click=reset_personal_model,
                 width="stretch")
    if personal:
        rows = [r for r in (before_after(n) for n in ("dev", "body", "heldout")) if r]
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        note("Before = the shared model; after = retrained with your corrections. Corrections are never part of "
             "the test sets, so these are fair comparisons. With only a few corrections, expect small changes.")

    # 9. Fairness ----------------------------------------------------------------
    heading("Fairness and bias", "Does ORBIT work equally well for everyone?")
    fair_table = predictions("heldout", datasets.file_version("heldout"), mv) if heldout_n else \
        pd.concat([predictions("dev", datasets.file_version("dev"), mv),
                   predictions("body", datasets.file_version("body"), mv)])
    source = "held-out set" if heldout_n else "development + body sets (author-written, so only a first look)"
    left, right = st.columns(2, gap="medium")
    left.html(f'<div class="field-label">By language · {esc(source)}</div>')
    left.dataframe(evaluation.by_group(fair_table, "language", "live"), hide_index=True, width="stretch")
    right.html(f'<div class="field-label">By writing style · {esc(source)}</div>')
    right.dataframe(evaluation.by_group(fair_table, "style", "live"), hide_index=True, width="stretch")
    note("<b>Known sources of bias:</b> the base model was trained on English Reddit comments, so its idea of "
         "emotions reflects mostly adult, Western, English-speaking internet users. ORBIT's own training "
         "sentences were written by one author, and the Hindi sample is small. Small groups (for example Hindi "
         "here) give unstable scores: a single mistake changes them a lot.")

    # 10. Impact study -------------------------------------------------------------
    heading("Impact study", "An early signal, not proof",
            "Each Calm Room session records mood before and after (1 = very low, 5 = great).")
    sessions = pd.DataFrame(storage.list_wellbeing())
    if sessions.empty:
        note("No sessions yet. Try the Calm Room, or load the demo journal on the Journal page.")
    else:
        sessions["change"] = sessions["after"] - sessions["before"]
        real = sessions[sessions["demo"] == 0]
        st.html(stats_html([(str(len(real)), "real sessions"), (str(int(sessions["demo"].sum())), "demo sessions"),
                            (f'{real["change"].mean():+.1f}' if len(real) else "–",
                             "average change (real sessions)")]))
        by_tool = sessions.groupby("tool", as_index=False)[["before", "after"]].mean().melt(
            id_vars="tool", var_name="when", value_name="mood")
        chart = alt.Chart(by_tool).mark_bar(cornerRadius=5).encode(
            x=alt.X("tool:N", title=None), xOffset="when:N",
            y=alt.Y("mood:Q", title="Average mood (1-5)", scale=alt.Scale(domain=[0, 5])),
            color=alt.Color("when:N", title=None, scale=alt.Scale(domain=["before", "after"],
                                                                  range=["#B9C8EA", "#8E7BBF"])))
        with st.container(key="glass-impact"):
            st.altair_chart(style(chart.properties(height=220)), width="stretch")
    note("<b>How to read this honestly:</b> moods are self-reported, the sample is small, there is no "
         "comparison group, and people who feel better may simply be more likely to finish a session. So this "
         "is an early signal, not evidence that ORBIT works. Testing with classmates needs teacher permission, "
         "voluntary participation and anonymous data.")
    with st.container(key="glass-feedback"):
        st.html('<div class="eyebrow">Feedback</div>')
        st.select_slider("How helpful was ORBIT today?", options=[1, 2, 3, 4, 5], value=4, key="fb_rating",
                         format_func={1: "Not at all", 2: "A little", 3: "Somewhat", 4: "Helpful",
                                      5: "Very helpful"}.get)
        st.text_input("Anything you'd like to tell the creator? (optional, please no names)", key="fb_comment")
        st.button("Send feedback", key="fb_send", on_click=submit_feedback)
        feedback = storage.list_feedback()
        if feedback:
            average = sum(f["rating"] for f in feedback) / len(feedback)
            st.html(f'<p class="body">{len(feedback)} response{"s" if len(feedback) != 1 else ""} · '
                    f"average {average:.1f} / 5</p>")

    # 11. Model card -------------------------------------------------------------
    _, _, meta = current_head()
    st.html(
        '<div class="section-head"><div class="eyebrow">Model card</div>'
        '<div class="title-sm" style="font-size:1.9rem">About the models</div></div>'
        '<div class="model-card">'
        "<div><span>Base model</span>SamLowe/roberta-base-go_emotions-onnx (quantized, ~125 MB, MIT licence); "
        "28 independent emotion scores; trained on ~58,000 English Reddit comments (GoEmotions)</div>"
        f"<div><span>ORBIT classifier</span>Variant {adopted_variant()}: softmax regression on the base model's "
        f"scores{' (for the original AND the dictionary-translated text)' if meta.get('uses_dictionary') else ''} "
        f"+ hashed word and character n-grams; trained on {meta['train_sentences']} sentences; regularisation {meta['l2']} chosen "
        f"by 5-fold cross-validation (macro-F1 {meta['cv_macro_f1']:.2f}); written in NumPy</div>"
        "<div><span>Runs</span>Offline on the laptop's CPU; no data leaves the device</div>"
        "<div><span>Safety</span>Deterministic rules checked before any reply; crisis text is never stored</div>"
        "<div><span>Limitations</span>Author-written training data; small Hindi sample; can misread sarcasm "
        "and very short messages; the held-out set is needed for a fair final score</div>"
        "<div><span>Not for</span>Diagnosis. ORBIT supports wellbeing; it does not replace professionals</div>"
        "</div>"
    )
