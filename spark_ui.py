"""
spark_ui.py
Create -> "I don't have an idea yet": the Spark path screens (spark.py has the method).

Six tappable questions, one at a time, with a progress trail. Every question has
"Surprise me" and "Skip". An optional 7th step asks for one word and how you feel.
Free text is checked for crisis wording first; if found, only the safety
response is shown. ORBIT never diagnoses from these answers; heavy choices only
bring a gentle mention of the Feel tab.
"""
import random

import streamlit as st

import spark
from components import esc, note, section_header
from studio import save_stars

STEPS = ["Medium", "Feeling", "Setting", "Era", "Contrast", "Texture", "One word"]
KEYS = ["medium", "emotions", "setting", "era", "contrast", "texture", None]


def answers():
    return st.session_state.setdefault("spark_answers", {})


def options(step):
    if step == 1:
        return spark.MEDIUMS
    if step == 2:
        return list(spark.EMOTIONS)
    if step == 3:
        return [s["text"] for s in spark.seeds("setting")]
    if step == 4:
        return list(spark.ERAS)
    if step == 5:
        return [s["text"] for s in spark.seeds("contrast")]
    if step == 6:
        return [s["text"] for s in spark.seeds("texture")]
    return []


def go(step):
    st.session_state.spark_step = step


def answer(step, value):
    answers()[KEYS[step - 1]] = value
    go(step + 1)


def surprise(step):
    rng = random.Random()
    choice = rng.choice(options(step))
    answer(step, [choice] if step == 2 else choice)


def skip(step):
    answers().pop(KEYS[step - 1], None)
    go(step + 1)


def take_pills(step, key):
    value = st.session_state.get(key)
    if value:
        answer(step, list(value)[:2] if step == 2 else value)


def finish():
    """After step 7: crisis check on the free text, then the three ideas."""
    word = st.session_state.get("spark_word", "").strip()
    from create_ui import block, crisis_in
    if crisis_in(word):
        block()
        st.session_state.spark_step = None
        return
    if word:
        answers()["word"] = word
    if st.session_state.get("spark_feeling_now"):
        answers()["feeling_now"] = st.session_state.spark_feeling_now
    st.session_state.spark_seed = 0
    st.session_state.spark_ideas = spark.three_ideas(answers())
    st.session_state.spark_step = 8


def trail(current):
    items = []
    for number, label in enumerate(STEPS, 1):
        state = "done" if number < current else "active" if number == current else ""
        items.append(f'<div class="step {state}"><span>{number}</span><small>{label}</small></div>')
    return '<div class="flow-steps">' + "".join(items) + "</div>"


def question(step):
    st.html(trail(step))
    with st.container(key=f"glass-spark-q{step}"):
        st.html(f'<div class="eyebrow">Question {step} of 6{" · optional" if step == 7 else ""}</div>'
                f'<div class="title-sm">{esc(spark.QUESTIONS[step - 1])}</div>')
        if step == 2:
            st.pills("Feelings", options(2), selection_mode="multi", key="spark_pick_2", label_visibility="collapsed")
            st.button("Next", key="spark_next_2", type="primary", on_click=take_pills, args=(2, "spark_pick_2"))
        elif step == 3:
            setting_tiles()
        elif step == 7:
            st.text_input("One word on your mind (optional)", key="spark_word", max_chars=30)
            st.pills("How are you feeling right now? (optional)", spark.FEELINGS_NOW, key="spark_feeling_now")
            st.button("Show me three ideas", key="spark_finish", type="primary", on_click=finish)
        else:
            st.pills("Options", options(step), key=f"spark_pick_{step}", label_visibility="collapsed",
                     on_change=take_pills, args=(step, f"spark_pick_{step}"))
        if step != 7:
            a, b, c = st.columns(3)
            a.button("Surprise me", key=f"spark_surprise_{step}", on_click=surprise, args=(step,), width="stretch")
            b.button("Skip", key=f"spark_skip_{step}", on_click=skip, args=(step,), width="stretch")
            if step > 1:
                c.button("Back", key=f"spark_back_{step}", on_click=go, args=(step - 1,), width="stretch")


def setting_tiles():
    """Settings as visual tiles: 9 at a time, with a way to see others."""
    places = spark.seeds("setting")
    offset = st.session_state.get("spark_tile_offset", 0)
    shown = [places[(offset + i) % len(places)] for i in range(9)]
    for row in range(3):
        for col, place in zip(st.columns(3), shown[row * 3:row * 3 + 3]):
            colours = place["tile"].split("|") if place["tile"] else ["#C9B9E8", "#B9C8EA"]
            with col:
                st.html(f'<div class="spark-tile" style="background:linear-gradient(135deg,{colours[0]},'
                        f'{colours[-1]})"><span>{esc(place["text"])}</span></div>')
                st.button("Choose", key=f"spark_place_{offset}_{row}_{place['text']}", on_click=answer,
                          args=(3, place["text"]), width="stretch")
    st.button("Show other places", key="spark_more", type="tertiary",
              on_click=lambda: st.session_state.update(spark_tile_offset=(offset + 9) % len(places)))


# ---------------------------------------------------------------
# The three ideas
# ---------------------------------------------------------------
def replace_idea(index, new):
    st.session_state.spark_ideas[index] = new


def remix_click(index):
    idea = st.session_state.spark_ideas[index]
    element = st.session_state.get(f"spark_el_{index}", "setting")
    st.session_state.spark_seed = st.session_state.get("spark_seed", 0) + 1
    replace_idea(index, spark.remix(idea, element, answers(), st.session_state.spark_seed))


def lock_click(index):
    idea = st.session_state.spark_ideas[index]
    element = st.session_state.get(f"spark_el_{index}", "setting")
    st.session_state.spark_seed = st.session_state.get("spark_seed", 0) + 1
    replace_idea(index, spark.lock(idea, element, answers(), st.session_state.spark_seed))


def use_idea(index):
    from create_ui import generate
    idea = st.session_state.spark_ideas[index]
    st.session_state.spark_step = None
    generate(spark.to_vector(idea, answers()), {"Safe": 0.3, "Bold": 0.6, "Weird": 0.9}[idea["direction"]],
             label=f"Spark idea · {idea['direction']}")


def ideas_screen():
    section_header("Create", "Three ideas for you", "Use one, remix one part, or lock one part and change the "
                   "rest.", first=True)
    if spark.heavy(answers()):
        note("Some of what you picked sounds heavy. That can make powerful work. If it's also how you feel right "
             "now, the <b>Feel</b> tab is here for you too.")
    for index, idea in enumerate(st.session_state.spark_ideas):
        with st.container(key=f"glass-idea-{index}"):
            st.html(f'<div class="eyebrow">{esc(idea["direction"])} · {esc(idea["medium"])}</div>'
                    f'<div class="title-sm" style="font-size:1.7rem">{esc(idea["title"])}</div>'
                    f'<p class="body" style="color:var(--charcoal);font-size:1rem">{esc(idea["logline"])}</p>'
                    f'<p class="body"><i>Why this idea:</i> {esc(idea["why"])}</p>')
            a, b, c, d = st.columns([1.3, 1.2, 1, 1], vertical_alignment="bottom")
            a.button("Use this idea", key=f"spark_use_{index}", type="primary", on_click=use_idea, args=(index,),
                     width="stretch")
            b.selectbox("Part", spark.ELEMENTS, index=1, key=f"spark_el_{index}", format_func=str.capitalize)
            c.button("Remix", key=f"spark_remix_{index}", on_click=remix_click, args=(index,), width="stretch",
                     help="Change only this part")
            d.button("Lock", key=f"spark_lock_{index}", on_click=lock_click, args=(index,), width="stretch",
                     help="Keep only this part and change the rest")
            left, right = st.columns(2)
            with left:
                st.html('<span class="feedback-label">Would you actually make this?</span>')
                st.feedback("stars", key=f"fb_make_{index}_{idea['title']}", on_change=save_stars,
                            args=("idea_make", idea["direction"], f"fb_make_{index}_{idea['title']}"))
            with right:
                st.html('<span class="feedback-label">Does it match your answers?</span>')
                st.feedback("stars", key=f"fb_match_{index}_{idea['title']}", on_change=save_stars,
                            args=("idea_match", idea["direction"], f"fb_match_{index}_{idea['title']}"))
    a, b = st.columns(2)
    a.button("Answer again", key="spark_restart", on_click=restart, width="stretch")
    b.button("Back to Create", key="spark_exit", on_click=leave, width="stretch")


def restart():
    st.session_state.spark_answers = {}
    st.session_state.spark_ideas = None
    st.session_state.spark_step = 1


def leave():
    st.session_state.spark_step = None


def spark_screen():
    step = st.session_state.spark_step
    if step >= 8 and st.session_state.get("spark_ideas"):
        ideas_screen()
        return
    section_header("Create", "Let's find a spark", "Six quick taps. Skip anything, or let ORBIT surprise you.",
                   first=True)
    question(min(step, 7))
    st.button("Back to Create", key="spark_leave", type="tertiary", on_click=leave)
