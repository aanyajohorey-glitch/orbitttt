"""
fonts.py
Typography pairing from data/fonts.csv (77 open-licence Google Fonts, each
tagged with mood numbers: vintage, bold, energy and warmth, from -1 to +1).

Rule (explainable):
1. The heading font is the heading-capable font closest to the vibe
   (smallest distance on vintage, bold, energy and warmth).
2. The body font must be easy to read, so it is chosen from body fonts, closest
   to a CALMER version of the vibe, and from a different category (a serif
   heading gets a sans body and the other way round) for contrast.
3. Devanagari-friendly fonts are preferred when the idea was written in Hindi.
4. "More font ideas": the next closest fonts, at most two from each category,
   so the list shows real variety (serif, sans, script, display, mono).
"""
from pathlib import Path

import pandas as pd
import streamlit as st

FONTS = Path(__file__).parent / "data" / "fonts.csv"


@st.cache_data
def load_fonts():
    table = pd.read_csv(FONTS)
    table["tag_list"] = table["tags"].str.split("|")
    return table


def _distance(row, vintage, bold, energy, warmth):
    return ((row["vintage"] - vintage) ** 2 + (row["bold"] - bold) ** 2 + (row["energy"] - energy) ** 2
            + 0.5 * (row["warmth"] - warmth) ** 2)


def pair(vintage, bold, energy, warmth=0.0, hindi=False):
    """Returns {"heading", "body", "feel", "why"}."""
    table = load_fonts()
    headings = table[table["use"].isin(["heading", "both"])].copy()
    headings["d"] = headings.apply(_distance, axis=1, args=(vintage, bold, energy, warmth))
    devanagari = headings["tag_list"].apply(lambda t: "devanagari" in t)
    headings.loc[devanagari, "d"] += -0.6 if hindi else 0.6
    heading = headings.sort_values("d").iloc[0]

    bodies = table[table["use"].isin(["body", "both"]) & (table["family"] != heading["family"])].copy()
    bodies["d"] = bodies.apply(_distance, axis=1, args=(vintage * 0.5, min(bold, 0.0), energy * 0.3, warmth))
    bodies.loc[bodies["category"] == heading["category"], "d"] += 0.5
    bodies.loc[bodies["tag_list"].apply(lambda t: "readable" in t), "d"] -= 0.1
    bodies.loc[bodies["category"].isin(["mono", "script"]), "d"] += 0.6
    if hindi:
        bodies.loc[bodies["tag_list"].apply(lambda t: "devanagari" in t), "d"] -= 0.6
    body = bodies.sort_values("d").iloc[0]

    feel = " and ".join(heading["tag_list"][:2])
    why = (f"{heading['family']} ({heading['category']}) is the heading font closest to your vibe "
           f"(vintage {vintage:+.1f}, bold {bold:+.1f}, energy {energy:+.1f}); {body['family']} "
           f"({body['category']}) is a calm, readable partner from a different family of letters.")
    more = alternatives(vintage, bold, energy, warmth, exclude={heading["family"], body["family"]}, hindi=hindi)
    return {"heading": heading["family"], "body": body["family"], "feel": feel, "why": why, "more": more}


def alternatives(vintage, bold, energy, warmth=0.0, exclude=(), size=8, hindi=False):
    """Other fonts close to the vibe: [{"family", "category", "feel"}], up to 2 per category."""
    table = load_fonts()
    table = table[~table["family"].isin(set(exclude))].copy()
    table["d"] = table.apply(_distance, axis=1, args=(vintage, bold, energy, warmth))
    if not hindi:
        table.loc[table["tag_list"].apply(lambda t: "devanagari" in t), "d"] += 0.6
    chosen, per_category = [], {}
    for _, row in table.sort_values("d").iterrows():
        if per_category.get(row["category"], 0) >= 2:
            continue
        per_category[row["category"]] = per_category.get(row["category"], 0) + 1
        chosen.append({"family": row["family"], "category": row["category"], "feel": " and ".join(row["tag_list"][:2])})
        if len(chosen) == size:
            break
    return chosen


def gallery_html(fonts_used, sample):
    """Font cards, each written IN its own font: the chosen pair first, then more ideas."""
    from html import escape
    cards = [(fonts_used["heading"], "Heading", fonts_used.get("feel", "")), (fonts_used["body"], "Body text", "")]
    cards += [(f["family"], f["category"].capitalize(), f["feel"]) for f in fonts_used.get("more", [])]
    html = []
    for family, role, feel in cards:
        face = f"font-family:'{family}'"
        html.append(f'<div class="font-card"><div class="font-aa" style="{face}">Aa</div>'
                    f'<div class="font-sample" style="{face}">{escape(sample)}</div>'
                    f'<div class="font-name" style="{face}">{escape(family)}</div>'
                    f'<small>{escape(role)}{" · " + escape(feel) if feel else ""}</small></div>')
    return '<div class="font-grid">' + "".join(html) + "</div>"


def families_in(fonts_used):
    return [fonts_used["heading"], fonts_used["body"]] + [f["family"] for f in fonts_used.get("more", [])]


def google_fonts_css(*families):
    """An @import rule that loads the fonts from Google Fonts (open licences)."""
    query = "&".join("family=" + f.replace(" ", "+") for f in dict.fromkeys(families))
    return f"@import url('https://fonts.googleapis.com/css2?{query}&display=swap');"
