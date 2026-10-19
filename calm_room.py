"""
calm_room.py
The Calm Room: four evidence-based coping tools.

  Breathing        - paced breathing with a glowing planet (box, 4-7-8, calm)
  Grounding        - the 5-4-3-2-1 senses exercise for anxiety and anger
  Thought Reframe  - a CBT (cognitive behavioural therapy) thought record;
                     ORBIT spots thinking traps and uses the emotion model to
                     show how the feeling changes after reframing
  Gratitude Jar    - noticing three good things

Every session asks "How do you feel?" before and after. Those answers are
saved (on this computer only) and become the impact study on the AI Lab page.
"""
import re

import streamlit as st

import storage
from analysis import earn_token, flash
from components import esc, note, section_header
from emotion_model import detect_emotions
from hinglish import to_english

TOOLS = ["Breathing", "Grounding", "Thought Reframe", "Gratitude Jar"]
TOOL_INFO = {
    "Breathing": "Slow, paced breathing calms the body's stress response.",
    "Grounding": "Naming what your senses notice brings you back to the present moment.",
    "Thought Reframe": "A thought record from CBT: catch a thought, test it, and find a kinder, truer one.",
    "Gratitude Jar": "Noticing good things, even small ones, gently lifts mood over time.",
}
MOOD_SCALE = {1: "Very low", 2: "Low", 3: "Okay", 4: "Good", 5: "Great"}

# ---------------------------------------------------------------
# Breathing patterns: (label, seconds, orb size at the END of the phase)
# ---------------------------------------------------------------
PATTERNS = {
    "Box 4-4-4-4": [("Breathe in", 4, 1.0), ("Hold", 4, 1.0), ("Breathe out", 4, 0.62), ("Hold", 4, 0.62)],
    "Calm 4-6": [("Breathe in", 4, 1.0), ("Breathe out", 6, 0.62)],
    "Relax 4-7-8": [("Breathe in", 4, 1.0), ("Hold", 7, 1.0), ("Breathe out", 8, 0.62)],
}


def pattern_key(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def breathing_css():
    """CSS animations for each breathing pattern, built from the timings above."""
    css = []
    for name, phases in PATTERNS.items():
        key = pattern_key(name)
        total = sum(seconds for _, seconds, _ in phases)
        # The orb grows and shrinks
        frames, elapsed, size = ["0% { transform: scale(0.62); }"], 0, 0.62
        for _, seconds, end_size in phases:
            elapsed += seconds
            frames.append(f"{elapsed / total * 100:.2f}% {{ transform: scale({end_size}); }}")
        css.append(f"@keyframes orb-{key} {{ {' '.join(frames)} }}")
        css.append(f".breath-{key} .breath-orb {{ animation: orb-{key} {total}s ease-in-out infinite; }}")
        # Each label is visible only during its own phase
        start = 0
        for index, (_, seconds, _) in enumerate(phases):
            a, b = start / total * 100, (start + seconds) / total * 100
            css.append(
                f"@keyframes label-{key}-{index} {{ 0% {{ opacity: 0; }} {max(a - 0.01, 0):.2f}% {{ opacity: 0; }} "
                f"{a + 0.5:.2f}% {{ opacity: 1; }} {b - 0.5:.2f}% {{ opacity: 1; }} {b:.2f}% {{ opacity: 0; }} "
                f"100% {{ opacity: 0; }} }}"
            )
            css.append(f".breath-{key} .breath-label-{index} {{ animation: label-{key}-{index} {total}s linear infinite; }}")
            start += seconds
    return "\n".join(css)


def breathing_html(name):
    key = pattern_key(name)
    labels = "".join(
        f'<span class="breath-label breath-label-{i}">{esc(label)}</span>'
        for i, (label, _, _) in enumerate(PATTERNS[name])
    )
    return (
        f'<div class="breath breath-{key}"><div class="breath-halo"></div>'
        f'<div class="breath-orb"><div class="sphere"></div></div>'
        f'<div class="breath-labels">{labels}</div></div>'
    )


# ---------------------------------------------------------------
# Thought Reframe: thinking traps (CBT "cognitive distortions")
# ---------------------------------------------------------------
THINKING_TRAPS = {
    "All-or-nothing thinking": (["always", "never", "completely", "totally", "nothing", "everything", "perfect"],
                                "Seeing things as all good or all bad, with nothing in between."),
    "Overgeneralising": (["everyone", "nobody", "no one", "everybody", "every time"],
                         "Turning one event into a rule about everything."),
    "Catastrophising": (["worst", "ruined", "disaster", "terrible", "end of the world", "fail everything"],
                        "Jumping to the worst possible outcome."),
    "Should statements": (["should", "must", "have to", "supposed to"],
                          "Holding yourself to rigid rules that create guilt or pressure."),
    "Mind reading": (["they think", "everyone thinks", "they must think", "judging me", "hates me"],
                     "Assuming you know what others are thinking."),
    "Labelling": (["i'm stupid", "i am stupid", "i'm a failure", "i am a failure", "i'm useless", "loser",
                   "i'm not good enough", "i am not good enough"],
                  "Putting a harsh label on yourself instead of describing what happened."),
}


def find_thinking_traps(thought):
    clean = " " + thought.lower().replace("’", "'") + " "
    found = []
    for trap, (words, meaning) in THINKING_TRAPS.items():
        hits = [w for w in words if re.search(rf"(?<!\w){re.escape(w)}(?!\w)", clean)]
        if hits:
            found.append((trap, meaning, hits))
    return found


NEGATIVE = ["sadness", "fear", "nervousness", "anger", "annoyance", "disappointment", "grief", "remorse",
            "embarrassment", "disgust", "disapproval"]


def heaviness(text):
    """How 'heavy' a thought feels to the model: the strongest negative emotion."""
    scores = dict(detect_emotions(to_english(text)[0]))
    label = max(NEGATIVE, key=lambda e: scores[e])
    return label, scores[label]


# ---------------------------------------------------------------
# Saving a session
# ---------------------------------------------------------------
def finish_session(tool):
    before = st.session_state.get("calm_before", 3)
    after = st.session_state.get("calm_after", 3)
    storage.add_wellbeing(tool, before, after)
    change = after - before
    message = (f"Your mood moved from {MOOD_SCALE[before]} to {MOOD_SCALE[after]}." if change
               else f"You stayed at {MOOD_SCALE[after]}. Showing up still counts.")
    flash(f"{tool} saved. {message}")
    earn_token("for looking after yourself")
    st.session_state.calm_done = tool


def mood_slider(label, key):
    st.select_slider(label, options=list(MOOD_SCALE), value=st.session_state.get(key, 3),
                     format_func=MOOD_SCALE.get, key=key)


def calm_room_page():
    section_header(
        "Calm Room",
        "A quiet place to breathe",
        "Small, evidence-based exercises for big feelings. Pick one, take your time, and notice how you feel "
        "before and after.",
        first=True,
    )
    if "calm_tool" not in st.session_state or st.session_state.calm_tool not in TOOLS:
        st.session_state.calm_tool = "Breathing"
    tool = st.pills("Choose an exercise", TOOLS, key="calm_tool") or "Breathing"
    st.html(f'<p class="body" style="margin:.2rem 0 1rem">{esc(TOOL_INFO[tool])}</p>')

    with st.container(key="glass-calm-before"):
        mood_slider("How do you feel right now?", "calm_before")

    with st.container(key="glass-calm-tool"):
        if tool == "Breathing":
            breathing_tool()
        elif tool == "Grounding":
            grounding_tool()
        elif tool == "Thought Reframe":
            reframe_tool()
        else:
            gratitude_tool()

    with st.container(key="glass-calm-after"):
        mood_slider("And how do you feel now?", "calm_after")
        st.button("Save this session", key="calm_finish", type="primary", on_click=finish_session, args=(tool,))
    if st.session_state.get("calm_done") == tool:
        note("Session saved to your private wellbeing log. It counts towards the impact study in the AI Lab.")


def breathing_tool():
    pattern = st.pills("Pattern", list(PATTERNS), key="breath_pattern") or "Calm 4-6"
    total = sum(seconds for _, seconds, _ in PATTERNS[pattern])
    st.html(breathing_html(pattern))
    st.html(f'<p class="body" style="text-align:center">Follow the planet: one full breath takes {total} seconds. '
            "Try five slow breaths, then come back to the slider below.</p>")


def grounding_tool():
    senses = [("5", "things you can see"), ("4", "things you can touch"), ("3", "things you can hear"),
              ("2", "things you can smell"), ("1", "thing you can taste")]
    done = 0
    for number, label in senses:
        value = st.text_input(f"{number} {label}", key=f"ground_{number}",
                              placeholder="Take your time…")
        done += bool(value.strip())
    st.progress(done / 5, text=f"{done} of 5 senses")
    if done == 5:
        st.html('<div class="calm-complete">You\'re here, in this moment. Notice your feet on the floor '
                "and take one slow breath.</div>")


def reframe_tool():
    st.text_area("What happened?", key="reframe_situation", height=80,
                 placeholder="e.g. I got a low mark in my maths test.")
    thought = st.text_area("What thought went through your mind?", key="reframe_thought", height=80,
                           placeholder="e.g. I always fail. I'm never going to be good at this.")
    if thought.strip():
        traps = find_thinking_traps(thought)
        if traps:
            items = "".join(
                f'<div class="trap"><b>{esc(t)}</b> <span>({esc(", ".join(h))})</span><br>{esc(m)}</div>'
                for t, m, h in traps
            )
            st.html(f'<div class="field-label">Possible thinking traps</div>{items}')
        else:
            st.html('<p class="body">No common thinking traps spotted. That thought may simply be honest.</p>')
    st.text_area("Evidence that the thought might NOT be completely true", key="reframe_evidence", height=80,
                 placeholder="e.g. I passed the last two tests. One test isn't the whole year.")
    balanced = st.text_area("A kinder, more balanced thought", key="reframe_balanced", height=80,
                            placeholder="e.g. This test went badly, but I can ask for help and improve.")
    if thought.strip() and balanced.strip() and st.button("See how the feeling changes", key="reframe_compare"):
        with st.spinner("Asking the emotion model…"):
            # Compare the SAME emotion before and after (the original thought's heaviest one)
            label_a, before = heaviness(thought)
            label_after_score = dict(detect_emotions(to_english(balanced)[0]))[label_a]
        st.html(
            '<div class="reframe-result reveal"><div class="field-label">What the emotion model sees</div>'
            f'<div class="reframe-bars"><div><span>Original thought</span><div class="emo-track"><i style="width:'
            f'{max(round(before * 100), 1)}%"></i></div><b>{label_a} {before:.0%}</b></div>'
            f'<div><span>Balanced thought</span><div class="emo-track"><i style="width:'
            f'{max(round(label_after_score * 100), 1)}%"></i></div><b>{label_a} {label_after_score:.0%}</b></div>'
            "</div></div>"
        )


def gratitude_tool():
    items = [st.text_input(f"Good thing {i}", key=f"grat_{i}", placeholder="Something small counts too…")
             for i in (1, 2, 3)]
    filled = [item for item in items if item.strip()]
    stars = "".join(f'<span class="jar-star" style="--i:{i}" title="{esc(t)}"></span>' for i, t in enumerate(filled))
    st.html(f'<div class="jar"><div class="jar-lid"></div><div class="jar-glass">{stars}</div>'
            f'<div class="jar-label">{len(filled)} of 3</div></div>')
