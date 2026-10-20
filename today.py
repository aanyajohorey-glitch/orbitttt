"""
today.py
The "Today" tab: ORBIT's guided check-in, one calm step at a time.

    1. Check in       - write (or speak) how you feel, and how you are right now (1-5)
    2. What I noticed - the feeling ORBIT detected, how sure it is, and a way to correct it
    3. ORBIT's reply  - the companion reflects and validates
    4. Try this       - ONE small, suggested action (breathing, grounding, ...)
    5. How now?       - mood after (1-5), saved for the impact study
    6. Your planet    - the check-in joins your galaxy, with its aesthetic world

Crisis messages stop after step 3: only help is shown (no tools, worlds or games).
"""
import streamlit as st

import calm_room
import demo_mode
import storage
from analysis import analyse, earn_token, flash, games_allowed, record_checkin
from companion import companion_card_html, reply, suggestion
from components import esc, field_html, go_to, note, save_world, swatches_html, tags_html
from feedback_ui import thumbs
from journal import entry_planet
from nudges import nudge_card
from safety import safety_card_html
from teach_ui import clarify, confidence_html, teach_panel
from views import (final_stats_html, greeting, hero_html, keep_talking, open_in_lab, other_emotions_html,
                   refresh_home, save_home_name, understood_html, voice_input)
from world_data import INTENTS, get_world, prompt_for

STEPS = ["Check in", "What I noticed", "ORBIT's reply", "Try this", "How now?", "Your planet"]
MOOD_SCALE = calm_room.MOOD_SCALE


def steps_html(current):
    """The little progress path at the top of Today."""
    items = []
    for number, label in enumerate(STEPS, 1):
        state = "done" if number < current else "active" if number == current else ""
        items.append(f'<div class="step {state}"><span>{number}</span><small>{esc(label)}</small></div>')
    return '<div class="flow-steps">' + "".join(items) + "</div>"


def step_title(number, title, text=""):
    st.html(f'<div class="step-head"><span class="step-num">{number}</span><div>'
            f'<div class="title-sm">{esc(title)}</div>'
            + (f'<p class="body">{text}</p>' if text else "") + "</div></div>")


def new_checkin():
    for key in ("home_result", "today_done", "today_planet"):
        st.session_state[key] = None if key == "home_result" else False
    st.session_state.home_text = ""


def open_tools(tool):
    st.session_state.calm_tool = tool
    go_to("Calm Room")


def finish_today(tool):
    """Step 5: save mood before/after, give a token, reveal the planet."""
    before = st.session_state.get("today_before", 3)
    after = st.session_state.get("today_after_rating", 3)
    storage.add_wellbeing(f"Today · {tool}", before, after)
    change = after - before
    flash(f"Mood {MOOD_SCALE[before]} → {MOOD_SCALE[after]}." if change else "Thank you for checking in.")
    earn_token("for finishing today's check-in")
    st.session_state.today_done = True


def today_page():
    name = storage.get_setting("name", "")
    st.html(hero_html())
    result = st.session_state.home_result
    current = 1 if not result else 6 if st.session_state.get("today_done") else 3
    st.html(steps_html(current))

    # ---------------------------------------------------------------- 1. Check in
    with st.container(key="glass-composer"):
        st.html(
            f'<div class="eyebrow">{greeting(name)} · Step 1</div>'
            '<div class="display" style="font-size:clamp(1.8rem,3.4vw,2.5rem)">What does your world feel like today?</div>'
            '<p class="lede">Describe a feeling, a moment or a whole day, in English, Hinglish or Hindi. '
            "No names or personal details are needed.</p>"
        )
        if not name:
            st.text_input("What should ORBIT call you? (optional)", key="home_name", on_change=save_home_name,
                          max_chars=30, placeholder="A first name or a nickname")
        voice_input(target="home_text", key="home_voice")
        st.text_area("Your feelings", key="home_text", height=130,
                     placeholder="e.g. Exams finished today. I feel relieved but strangely empty…")
        if demo_mode.enabled():
            demo_mode.sample_buttons("home_text")
        left, right = st.columns([1.2, 1])
        with left:
            st.select_slider("How are you, right now?", options=list(MOOD_SCALE), value=3,
                             format_func=MOOD_SCALE.get, key="today_before")
        with right:
            st.pills("Creative intent · optional", INTENTS, key="home_intent")

        if st.button("Find my orbit", type="primary", key="find_orbit"):
            result = analyse(st.session_state.home_text.strip(),
                             empty_message="Write a few words about how you feel first.")
            if result:
                result["intent"] = st.session_state.home_intent or "Explore"
                result["reply"], result["style"] = reply(result, name=name)
                record_checkin(result, "Today")
            st.session_state.home_result = result
            st.session_state.today_done = False
            if result:
                st.rerun()   # redraw from step 1 with the new result (no rerun on a warning, so it stays visible)

    if not result:
        note("ORBIT is an AI, not a therapist. If you are ever in danger, call Tele-MANAS on 14416 or 112.")
        return

    # ---------------------------------------------------------------- crisis: help only
    if result["safety"] == "crisis":
        st.html(safety_card_html("crisis"))
        with st.container(key="glass-companion"):
            st.html(companion_card_html(result["reply"], result["style"]))
            st.button("Talk to ORBIT", key="home_talk", on_click=keep_talking, args=(result,))
        st.button("Start a new check-in", key="today_new", on_click=new_checkin)
        return

    # ---------------------------------------------------------------- 2. What I noticed
    with st.container(key="glass-noticed"):
        step_title(2, "What ORBIT noticed")
        st.html(confidence_html(result) + understood_html(result) + final_stats_html(result)
                + field_html("Also feeling", other_emotions_html(result["emotions"], result["final"]["emotion"])))
        clarify(result, key="home_clarify", on_update=refresh_home)
        left, right = st.columns([1, 1])
        with left:
            teach_panel(result, key="home_teach", on_update=refresh_home)
        right.button("See the full analysis", key="home_to_lab", on_click=open_in_lab, args=(result,),
                     type="tertiary")
    if result["safety"] == "concern":
        st.html(safety_card_html("concern"))

    # ---------------------------------------------------------------- 3. ORBIT's reply
    with st.container(key="glass-companion"):
        step_title(3, "ORBIT's reply")
        st.html(companion_card_html(result["reply"], result["style"]))
        left, right = st.columns([1, 1.4], vertical_alignment="center")
        left.button("Keep talking", key="home_talk", on_click=keep_talking, args=(result,), width="stretch")
        with right:
            thumbs("reply", result["style"], key="fb_today_reply")
    nudge_card(result)

    # ---------------------------------------------------------------- 4. Try this
    tool, line = suggestion(result)
    with st.container(key="glass-try"):
        step_title(4, f"One small thing to try · {tool}", esc(line))
        calm_room.render_tool(tool)
        st.button("Choose a different tool", key="home_tool", type="tertiary", on_click=open_tools, args=(tool,))

    # ---------------------------------------------------------------- 5. How now?
    with st.container(key="glass-after"):
        step_title(5, "How do you feel now?")
        st.select_slider("Right now I feel…", options=list(MOOD_SCALE), value=st.session_state.get("today_before", 3),
                         format_func=MOOD_SCALE.get, key="today_after_rating")
        if not st.session_state.get("today_done"):
            st.button("Finish check-in", key="today_finish", type="primary", on_click=finish_today, args=(tool,))
        else:
            thumbs("tool", tool, key=f"fb_today_tool_{tool}")

    # ---------------------------------------------------------------- 6. Your planet
    if st.session_state.get("today_done"):
        show_planet(result)


def show_planet(result):
    world = get_world(result["world"])
    prompt = prompt_for(world, result["intent"])
    with st.container(key="glass-planet"):
        step_title(6, "Your new planet joined your galaxy")
        left, right = st.columns([1, 1.8], vertical_alignment="center")
        with left:
            st.html('<div class="result-planet planet-arrive">'
                    + entry_planet(result["emotions"], result["final"]["emotion"], size=130) + "</div>")
        with right:
            st.html(
                f'<div class="eyebrow">Your world · {esc(world["mood"])}</div>'
                f'<div class="display" style="font-size:2.3rem;margin-top:.3rem">{esc(world["name"])}</div>'
                f'<p class="body">{esc(world["description"])}</p>'
                + field_html("Matched on", tags_html(result["matched"]))
                + field_html(f'Your prompt · {esc(result["intent"])}', f'<div class="prompt">{esc(prompt)}</div>')
                + field_html("Palette", swatches_html(world["palette"]))
            )
            a, b, c = st.columns(3)
            a.button("Save world", key="save_home_result", type="primary", on_click=save_world,
                     args=(world["name"], "Today", result["intent"], prompt, result["text"][:160]), width="stretch")
            b.button("See my galaxy", key="today_galaxy", on_click=go_to, args=("Journal",), width="stretch")
            c.button("New check-in", key="today_new", on_click=new_checkin, width="stretch")
    if games_allowed(result):
        note("You earned an arcade token for looking after yourself. Spend it in Tools → Arcade.")
