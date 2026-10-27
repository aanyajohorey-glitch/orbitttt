"""
components.py
Reusable building blocks for ORBIT's pages:
- HTML pieces such as planets, colour swatches and world cards
- functions that change the app's memory (st.session_state):
  switching pages, saving worlds and removing them
- the pop-up window that shows a world's details

The HTML only describes WHAT to show. How it looks comes from styles.py.
"""
import html
from datetime import datetime
from uuid import uuid4

import streamlit as st

import storage
from world_data import get_world


def esc(text):
    """Make text safe to place inside HTML (important for user input)."""
    return html.escape(str(text))


# ---------------------------------------------------------------
# HTML pieces
# ---------------------------------------------------------------
def planet_html(light, dark, size=96, ring=False, delay=0.0):
    """A glossy 3D-style planet made only with CSS gradients."""
    ring_back = '<div class="ring back"></div>' if ring else ""
    ring_front = '<div class="ring front"></div>' if ring else ""
    return (
        f'<div class="planet" style="--c1:{light};--c2:{dark};--size:{size}px;'
        f'animation-delay:-{delay}s">'
        f'{ring_back}<div class="sphere"></div>{ring_front}</div>'
    )


def world_planet(world, size=96, delay=0.0):
    """The planet that belongs to a world from worlds.csv."""
    return planet_html(world["planet_light"], world["planet_dark"], size, world["ring"], delay)


def swatches_html(palette):
    """A row of small colour squares."""
    squares = "".join(
        f'<span class="swatch" style="background:{colour}" title="{colour}"></span>'
        for colour in palette
    )
    return f'<div class="swatches">{squares}</div>'


def large_swatches_html(palette):
    """Bigger colour squares with their hex codes underneath."""
    squares = "".join(
        f'<div class="swatch-lg"><i style="background:{colour}"></i>{colour}</div>'
        for colour in palette
    )
    return f'<div class="swatches-lg">{squares}</div>'


def tags_html(items):
    """Small labels, e.g. the visual elements of a world."""
    return '<div class="tags">' + "".join(f'<span class="tag">{esc(item)}</span>' for item in items) + "</div>"


def field_html(label, value_html):
    """A small label with a value underneath it."""
    return f'<div class="field"><div class="field-label">{label}</div><div class="field-value">{value_html}</div></div>'


def world_card_html(world, delay=0.0, subtitle=None):
    """A planet card: planet, mood, name, short description and palette."""
    return (
        '<div class="world-card">'
        f'<div class="planet-stage">{world_planet(world, 92, delay)}</div>'
        f'<div class="eyebrow">{esc(subtitle or world["mood"])}</div>'
        f'<div class="world-name">{esc(world["name"])}</div>'
        f'<p class="world-desc">{esc(world["description"])}</p>'
        f'{swatches_html(world["palette"])}'
        "</div>"
    )


def section_header(eyebrow, title, text="", first=False):
    """The heading at the top of each section."""
    extra = " first" if first else ""
    lede = f'<p class="lede">{text}</p>' if text else ""
    st.html(
        f'<div class="section-head{extra}"><div class="eyebrow">{eyebrow}</div>'
        f'<div class="display">{title}</div>{lede}</div>'
    )


def note(text):
    """A quiet, honest note (for example: 'the model is not connected yet')."""
    st.html(f'<div class="note">{text}</div>')


# ---------------------------------------------------------------
# Session state helpers
# st.session_state is the app's short-term memory for this browser tab.
# Saved worlds are ALSO written to data/orbit.db (storage.py), so they
# survive a page refresh and an app restart.
# ---------------------------------------------------------------
def go_to(page):
    """Switch to another page (used by the navigation buttons)."""
    st.session_state.page = page


def save_world(world_name, source, intent, prompt, note_text="", constraint=""):
    """Add a world to My Collection (it also appears in ORBIT Universe)."""
    for item in st.session_state.collection:
        if item["world"] == world_name and item["prompt"] == prompt:
            st.session_state.flash.append(f"{world_name} is already in your collection.")
            return

    item = {
        "id": uuid4().hex[:8],
        "world": world_name,
        "source": source,
        "intent": intent,
        "prompt": prompt,
        "constraint": constraint,
        "note": note_text,
        "saved_at": datetime.now().strftime("%d %b, %H:%M"),
    }
    storage.add_collection_item(item)
    st.session_state.collection.append(item)
    st.session_state.flash.append(f"Saved {world_name} to your collection.")


def remove_world(item_id):
    """Remove one saved world from the collection."""
    storage.remove_collection_item(item_id)
    st.session_state.collection = [
        item for item in st.session_state.collection if item["id"] != item_id
    ]
    st.session_state.flash.append("Removed from your collection.")


# ---------------------------------------------------------------
# World details pop-up
# ---------------------------------------------------------------
@st.dialog("World details", width="large")
def world_dialog(item):
    """Show everything about one saved world in a pop-up window."""
    world = get_world(item["world"])
    if world is None:
        st.error("This world could not be found in data/worlds.csv.")
        return

    left, right = st.columns([1, 1.7])
    with left:
        st.html(f'<div class="result-planet">{world_planet(world, 150)}</div>')
    with right:
        details = (
            f'<div class="eyebrow">{esc(world["mood"])}</div>'
            f'<div class="title-sm" style="font-size:2rem">{esc(world["name"])}</div>'
            f'<p class="body">{esc(world["description"])}</p>'
            + field_html(f'Prompt · {esc(item["intent"])}', f'<div class="prompt">{esc(item["prompt"])}</div>')
        )
        if item["constraint"]:
            details += field_html("Constraint", esc(item["constraint"]))
        st.html(details)

    extra = (
        field_html("Palette", large_swatches_html(world["palette"]))
        + field_html("Visual elements", tags_html(world["elements"]))
        + field_html("Typography", esc(world["typography"]))
        + field_html("Sound vibe", esc(world["sound"]))
    )
    if item["note"]:
        extra += field_html("Your words", f"“{esc(item['note'])}”")
    extra += field_html("Saved", f'{esc(item["source"])} · {esc(item["saved_at"])}')
    st.html(extra)


# ---------------------------------------------------------------
# Shared page parts
# ---------------------------------------------------------------
def top_bar():
    st.html(
        '<div class="topbar"><div class="brand">'
        + planet_html("#E6DCF6", "#A895D2", 20)
        + '<span>ORBIT</span></div></div>'
    )


def footer():
    st.html(
        '<div class="footer"><span style="margin-left:auto">Class 12 CBSE Artificial Intelligence</span></div>'
    )
