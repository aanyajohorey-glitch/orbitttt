"""
vending.py
The Aesthetic Vending Machine: a real arcade-style vending machine.

How it works (a "state machine", like the chip inside a real one):

    idle  --insert token-->  credit  --type code + OK-->  vending
    vending (capsule falls)  -->  tray  --push flap-->  open (see your pack)

- Each capsule costs 1 arcade token. Tokens are EARNED by looking after
  yourself: a check-in on Home / Mood Lab / Companion or a Calm Room session.
- Bought slots show SOLD OUT until the machine is restocked.
- Sounds (coin, beep, motor, chime) are made with maths in soundscapes.py.
"""
import random

import streamlit as st

from components import esc, field_html, go_to, large_swatches_html, note, save_world, section_header, \
    tags_html, world_planet
from soundscapes import sfx
from world_data import CONSTRAINTS, INTENTS, get_world, load_worlds, prompt_for

ROWS, COLS = "ABC", "123"
CODES = [row + col for row in ROWS for col in COLS]
SLOT_COLOURS = dict(zip(CODES, ["#C9B9E8", "#B9C8EA", "#EBCBD7", "#C7D3C0", "#E3D3B8",
                                "#9C90B3", "#D6E4F0", "#F0D9C9", "#CFE3D9"]))


def make_pack(previous=None):
    """Pick a random world, intent and constraint for a creative pack."""
    worlds = load_worlds()
    world = random.choice(worlds)
    while previous and world["name"] == previous["world"] and len(worlds) > 1:
        world = random.choice(worlds)  # avoid the same world twice in a row
    return {"world": world["name"], "intent": random.choice(INTENTS), "constraint": random.choice(CONSTRAINTS)}


# ---------------------------------------------------------------
# Machine state
# ---------------------------------------------------------------
DEFAULT_STATE = {
    "vm_state": "idle",   # idle / vending / tray / open
    "vm_credit": False,   # is a token in the machine?
    "vm_code": "",        # what has been typed on the keypad
    "vm_slot": None,      # the slot being vended
    "vm_pack": None,      # the creative pack inside the capsule
    "vm_sold": [],        # empty slots
    "vm_message": None,   # a short LED message (e.g. SOLD OUT)
    "vm_sfx": None,       # a sound to play on the next run
    "vm_sfx_count": 0,
}


def ensure_state():
    for key, value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = list(value) if isinstance(value, list) else value


def play(sound):
    st.session_state.vm_sfx = sound
    st.session_state.vm_sfx_count += 1


def say(message, sound="error"):
    st.session_state.vm_message = message
    play(sound)


def insert_token():
    st.session_state.vm_message = None
    if st.session_state.vm_state not in ("idle", "open"):
        return say("PLEASE WAIT")
    if st.session_state.vm_credit:
        return say("CREDIT ALREADY IN")
    if st.session_state.tokens <= 0:
        return say("NO TOKENS LEFT")
    st.session_state.tokens -= 1
    st.session_state.vm_credit = True
    st.session_state.vm_state = "idle"
    st.session_state.vm_code = ""
    play("coin")


def return_token():
    st.session_state.vm_message = None
    if st.session_state.vm_credit:
        st.session_state.tokens += 1
        st.session_state.vm_credit = False
        st.session_state.vm_code = ""
        say("TOKEN RETURNED", "coin")


def press_key(key):
    st.session_state.vm_message = None
    if st.session_state.vm_state not in ("idle", "open"):
        return
    code = st.session_state.vm_code
    if key in ROWS:
        st.session_state.vm_code = key
        play("beep")
    elif len(code) == 1:
        st.session_state.vm_code = code + key
        play("beep")
    else:
        say("LETTER FIRST")


def clear_code():
    st.session_state.vm_code = ""
    st.session_state.vm_message = None
    play("beep")


def press_ok():
    st.session_state.vm_message = None
    code = st.session_state.vm_code
    if st.session_state.vm_state not in ("idle", "open"):
        return
    if not st.session_state.vm_credit:
        return say("INSERT TOKEN")
    if code not in CODES:
        return say("ENTER A CODE · e.g. B2")
    if code in st.session_state.vm_sold:
        st.session_state.vm_code = ""
        return say(f"{code} SOLD OUT")
    st.session_state.vm_pack = make_pack(st.session_state.vm_pack)
    st.session_state.vm_slot = code
    st.session_state.vm_sold.append(code)
    st.session_state.vm_credit = False
    st.session_state.vm_code = ""
    st.session_state.vm_state = "vending"
    play("vend")


def collect():
    if st.session_state.vm_state in ("vending", "tray"):
        st.session_state.vm_state = "open"
        play("chime")


def restock():
    if st.session_state.vm_state in ("vending", "tray"):
        return say("COLLECT FIRST")
    st.session_state.vm_sold = []
    say("RESTOCKED!", "coin")


# ---------------------------------------------------------------
# Drawing the machine
# ---------------------------------------------------------------
def led_text():
    s = st.session_state
    if s.vm_message:
        return s.vm_message, "", False
    if s.vm_state == "vending":
        return f"VENDING {s.vm_slot}…", "please wait", False
    if s.vm_state == "tray":
        return "TAKE YOUR CAPSULE", "push the flap below", True
    if s.vm_credit:
        if not s.vm_code:
            return "CREDIT 1", "select an item", True
        if len(s.vm_code) == 1:
            return f"SELECT  {s.vm_code}_", "now a number", True
        return f"{s.vm_code}  · PRESS OK", "", True
    if s.tokens <= 0:
        return "NO TOKENS", "check in or relax to earn one", True
    return "INSERT TOKEN", f"{s.tokens} token{'s' if s.tokens != 1 else ''} available", True


def machine_html():
    s = st.session_state
    slots = ""
    for code in CODES:
        classes = "vm-slot"
        if code in s.vm_sold and not (s.vm_state == "vending" and code == s.vm_slot):
            classes += " sold"
        if s.vm_state == "vending" and code == s.vm_slot:
            classes += " picking"
        typed = s.vm_code and code.startswith(s.vm_code) and s.vm_state in ("idle", "open")
        classes += " typed" if typed else ""
        slots += (
            f'<div class="{classes}"><div class="capsule" style="--c:{SLOT_COLOURS[code]}"></div>'
            f'<div class="vm-coil"></div><div class="vm-label">{code} · 1 token</div></div>'
        )
    bulbs = "".join("<span></span>" for _ in range(14))

    tray = ""
    if s.vm_state in ("vending", "tray"):
        arrive = " arrive" if s.vm_state == "vending" else ""
        tray = f'<div class="capsule{arrive}" style="--c:{SLOT_COLOURS[s.vm_slot]}"></div>'
    glow = " glow" if s.vm_state in ("vending", "tray") else ""

    return (
        '<div class="vm">'
        f'<div class="vm-marquee"><div class="vm-bulbs">{bulbs}</div>'
        '<div class="vm-title">ORBIT ARCADE</div><div class="vm-sub">aesthetic vending · est. 2026</div></div>'
        f'<div class="vm-window"><div class="vm-grid">{slots}</div><div class="vm-glare"></div></div>'
        f'<div class="vm-lower"><div class="vm-tray{glow}"><div class="vm-flap">PUSH</div>{tray}</div>'
        '<div class="vm-coin"><div class="vm-coin-slot"></div><span>TOKEN</span></div></div>'
        '<div class="vm-feet"><span></span><span></span></div>'
        "</div>"
    )


def led_html():
    big, small, blink = led_text()
    return (f'<div class="vm-led{" blink" if blink else ""}"><span>{esc(big)}</span>'
            f'<small>{esc(small)}</small></div>')


def tokens_html():
    tokens = st.session_state.tokens
    coins = "".join('<i class="vm-token"></i>' for _ in range(min(tokens, 8)))
    more = f"<b>+{tokens - 8}</b>" if tokens > 8 else ""
    return (f'<div class="vm-tokens"><span class="field-label">Your tokens · {tokens}</span>'
            f'<div>{coins or "<em>none yet</em>"}{more}</div></div>')


def play_sound():
    if st.session_state.vm_sfx and st.session_state.get("vm_sound", True):
        with st.container(key="sfx"):
            st.audio(sfx(st.session_state.vm_sfx, st.session_state.vm_sfx_count % 2),
                     format="audio/wav", autoplay=True)
    st.session_state.vm_sfx = None


def vending_machine():
    ensure_state()
    section_header(
        "Aesthetic Vending Machine",
        "Insert a token. Punch a code. Catch a world.",
        "Every capsule hides a world, a creative prompt and a small challenge. Tokens are earned by looking "
        "after yourself: each check-in or Calm Room session adds one.",
        first=True,
    )
    play_sound()

    machine_col, panel_col = st.columns([1.45, 1], gap="large")
    with machine_col:
        st.html(machine_html())
    with panel_col:
        with st.container(key="vm-panel"):
            st.html(led_html())
            st.session_state.vm_message = None   # like a real machine, messages flash once
            st.html(tokens_html())
            with st.container(key="vm-coinbtns"):
                left, right = st.columns(2)
                left.button("Insert token", key="vm_insert", type="primary", on_click=insert_token,
                            width="stretch")
                right.button("Return token", key="vm_return", on_click=return_token, width="stretch")
            with st.container(key="vm-keypad"):
                for row in (list(ROWS), list(COLS)):
                    for column, key in zip(st.columns(3), row):
                        column.button(key, key=f"kp_{key}", on_click=press_key, args=(key,), width="stretch")
                clr, ok = st.columns(2)
                clr.button("CLR", key="kp_clr", on_click=clear_code, width="stretch")
                ok.button("OK", key="kp_ok", type="primary", on_click=press_ok, width="stretch")
            st.toggle("Arcade sounds", key="vm_sound", value=True)
            st.button("Call the restocker", key="vm_restock", type="tertiary", on_click=restock)

    if st.session_state.vm_state in ("vending", "tray"):
        with st.container(key="vm-push"):
            st.button("PUSH the flap to collect your capsule", key="vm_collect", type="primary",
                      on_click=collect, width="stretch")
    if st.session_state.vm_state == "vending":
        st.session_state.vm_state = "tray"   # the fall animation plays only once

    if st.session_state.vm_state == "open" and st.session_state.vm_pack:
        show_pack(st.session_state.vm_pack, st.session_state.vm_slot)
    elif st.session_state.tokens <= 0 and not st.session_state.vm_credit and st.session_state.vm_state == "idle":
        note("Out of tokens? Check in on Home, talk to the Companion or try a Calm Room exercise to earn more.")
        left, right, _ = st.columns([1, 1, 2])
        left.button("Check in", key="vm_earn_home", on_click=go_to, args=("Home",), width="stretch")
        right.button("Calm Room", key="vm_earn_calm", on_click=go_to, args=("Calm Room",), width="stretch")


def show_pack(pack, slot):
    world = get_world(pack["world"])
    prompt = prompt_for(world, pack["intent"])
    with st.container(key="glass-pack"):
        left, right = st.columns([1, 1.9], vertical_alignment="center")
        with left:
            st.html(f'<div class="result-planet reveal">{world_planet(world, 150)}</div>')
        with right:
            st.html(
                '<div class="reveal">'
                f'<div class="eyebrow">Capsule {esc(slot)} · Creative pack</div>'
                f'<div class="display" style="font-size:2.3rem;margin-top:.35rem">{esc(world["name"])}</div>'
                f'<p class="body">{esc(world["mood"])}. {esc(world["description"])}</p>'
                + field_html(f'Prompt · {esc(pack["intent"])}', f'<div class="prompt">{esc(prompt)}</div>')
                + field_html("Constraint", esc(pack["constraint"]))
                + "</div>"
            )
        st.html(
            '<div class="meta-grid reveal">'
            + field_html("Palette", large_swatches_html(world["palette"]))
            + field_html("Visual elements", tags_html(world["elements"]))
            + field_html("Typography", esc(world["typography"]))
            + field_html("Sound vibe", esc(world["sound"]))
            + "</div>"
        )
        first, second = st.columns(2)
        first.button(
            "Save to collection", key="save_pack", type="primary", on_click=save_world,
            args=(world["name"], "Vending Machine", pack["intent"], prompt, "", pack["constraint"]),
            width="stretch",
        )
        second.button("Insert another token", key="vm_again", on_click=insert_token, width="stretch")
