"""
wrapped.py
My Galaxy -> Wrapped: your check-ins turned into art, like a year-in-review.

For the chosen period ORBIT shows:
    your top feelings and how many times you checked in
    a mood tracker (one point per day)
    a painting made from your emotion blend (every feeling family has colours)
    a playlist chosen for that blend
    the world and palette that matched you most
    a card to download and keep

Everything is made on this device from your own journal. The words are
"what your check-ins show", never a diagnosis.
"""
import io
import math
import random
from collections import Counter

import streamlit as st
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import music
import storage
from components import esc, go_to, note, section_header, swatches_html
from emotion_model import GROUP_COLOURS, GROUP_OF
from journal import entries_table
from patterns import daily, in_range, mood_line
from world_data import get_world

PERIODS = {"7 days": 7, "30 days": 30, "1 year": 365, "All time": None}
MIN_CHECKINS = 3


def pick(table, days):
    if days is None or table.empty:
        return table
    return in_range(table, days)


def blend(table):
    """All emotions added up over the period, strongest first: [(emotion, share), ...]."""
    totals = Counter()
    for emotions in table["emotions"]:
        for emotion, score in emotions:
            totals[emotion] += score
    whole = sum(totals.values()) or 1
    return [(emotion, value / whole) for emotion, value in totals.most_common()]


def family_blend(emotions):
    totals = Counter()
    for emotion, share in emotions:
        totals[GROUP_OF.get(emotion, "Neutral")] += share
    return totals.most_common()


def mood_words(average):
    if average > 0.25:
        return "mostly bright"
    if average < -0.25:
        return "often heavy"
    return "a mix of light and heavy"


def summary(table):
    """The numbers for the period (table: rows from journal.entries_table)."""
    emotions = blend(table)
    worlds = Counter(w for w in table["world"] if w)
    days = daily(table)
    brightest = days.sort_values("mood", ascending=False).iloc[0] if not days.empty else None
    return {
        "checkins": len(table),
        "days": table["date"].nunique(),
        "top_feelings": [e for e, _ in Counter(table["primary"]).most_common(3)],
        "families": family_blend(emotions),
        "emotions": emotions,
        "mood": float(table["mood"].mean()),
        "world": worlds.most_common(1)[0][0] if worlds else None,
        "brightest": brightest["date"].strftime("%d %b") if brightest is not None else None,
    }


def painting(families, seed=0, size=(900, 600)):
    """Abstract art from the emotion blend: a colour wash, soft clouds, flowing ribbons and a few sparks.
    Bigger feelings get more paint. The same check-ins always give the same painting."""
    rng = random.Random(seed)
    width, height = size
    colours = [(GROUP_COLOURS.get(f, GROUP_COLOURS["Neutral"]), share) for f, share in families if share > 0]
    if not colours:
        colours = [(GROUP_COLOURS["Neutral"], 1.0)]
    weights = [share for _, share in colours]
    top, bottom = _rgb(colours[0][0][0]), _rgb(colours[-1][0][0] if len(colours) > 1 else colours[0][0][1])
    canvas = Image.new("RGB", size)
    wash = ImageDraw.Draw(canvas)
    for y in range(height):
        t = y / height
        wash.line([(0, y), (width, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)))

    def layer(blur, draw_on):
        """Each colour gets its own mask, so blurred edges fade into the painting instead of going grey."""
        masks = {}

        def mask_for(colour):
            if colour not in masks:
                masks[colour] = Image.new("L", size, 0)
            return ImageDraw.Draw(masks[colour])
        draw_on(mask_for)
        for colour, mask in masks.items():
            canvas.paste(Image.new("RGB", size, colour), (0, 0), mask.filter(ImageFilter.GaussianBlur(blur)))

    def clouds(draw):
        for _ in range(36):
            light, dark = rng.choices(colours, weights)[0][0]
            r = rng.randint(width // 8, width // 3)
            x, y = rng.randint(-r, width), rng.randint(-r, height)
            draw(_rgb(rng.choice([light, dark]))).ellipse([x, y, x + r * 2, y + r * 1.3], fill=rng.randint(80, 150))

    def ribbons(draw):
        for _ in range(7):
            light, dark = rng.choices(colours, weights)[0][0]
            pen, alpha = draw(_rgb(dark)), rng.randint(130, 200)
            base_y = rng.uniform(0.15, 0.85) * height
            amplitude, waves, phase = rng.uniform(30, 110), rng.uniform(0.6, 1.8), rng.uniform(0, 6.3)
            thickness = rng.randint(10, 30)
            for step in range(0, width + 1, 3):
                x = step
                y = base_y + amplitude * math.sin(phase + waves * 2 * math.pi * x / width)
                r = thickness * (0.55 + 0.45 * math.sin(math.pi * x / width))
                pen.ellipse([x - r, y - r, x + r, y + r], fill=alpha)

    def sparks(draw):
        for _ in range(60):
            x, y, r = rng.randint(0, width), rng.randint(0, height), rng.choice([1, 1, 2, 3])
            draw((255, 255, 255)).ellipse([x - r, y - r, x + r, y + r], fill=rng.randint(120, 230))

    layer(40, clouds)
    layer(3, ribbons)
    layer(0.6, sparks)
    return canvas


def _rgb(hex_colour):
    hex_colour = hex_colour.lstrip("#")
    return tuple(int(hex_colour[i:i + 2], 16) for i in (0, 2, 4))


def card_png(facts, art, period, name=""):
    """A tall card to download: the painting, then the highlights."""
    card = Image.new("RGB", (1080, 1500), "#1D1832")
    card.paste(art.resize((1080, 720)), (0, 0))
    draw = ImageDraw.Draw(card)
    big, mid, small = (ImageFont.load_default(size=s) for s in (76, 42, 30))
    title = f"{name}'s ORBIT Wrapped" if name else "My ORBIT Wrapped"
    y = 770
    draw.text((70, y), title, font=big, fill="#FFFFFF")
    draw.text((70, y + 100), period, font=small, fill="#C9B9E8")
    lines = [
        ("Check-ins", f'{facts["checkins"]} on {facts["days"]} days'),
        ("Top feelings", ", ".join(f.capitalize() for f in facts["top_feelings"])),
        ("Overall", mood_words(facts["mood"])),
        ("Your world", facts["world"] or "Still exploring"),
    ]
    y += 180
    for label, value in lines:
        draw.text((70, y), label.upper(), font=small, fill="#A895D2")
        draw.text((70, y + 40), value, font=mid, fill="#FFFFFF")
        y += 120
    draw.text((70, 1430), "ORBIT · Every feeling has a universe.", font=small, fill="#8E84A8")
    buffer = io.BytesIO()
    card.save(buffer, format="PNG")
    return buffer.getvalue()


def png(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def wrapped_page():
    section_header("My Galaxy", "Your ORBIT Wrapped",
                   "Your check-ins, turned into a painting, a playlist and a palette.", first=True)
    period = st.segmented_control("Period", list(PERIODS), default="30 days", key="wrapped_period",
                                  label_visibility="collapsed") or "30 days"
    table = entries_table()
    table = pick(table, PERIODS[period])
    if table.empty or len(table) < MIN_CHECKINS:
        with st.container(key="glass-wrapped-empty"):
            st.html(f'<div class="title-sm">Not enough check-ins yet</div><p class="body">Wrapped needs at least '
                    f"{MIN_CHECKINS} check-ins in this period"
                    + (f" (you have {len(table)})" if len(table) else "") + ". Each check-in adds colour to "
                    "your painting and songs to your playlist.</p>")
            st.button("Check in now", key="wrapped_checkin", type="primary", on_click=go_to, args=("Home",))
        return

    facts = summary(table)
    seed = int(table["id"].sum()) if "id" in table else 0
    art = painting(facts["families"], seed=seed)
    world = get_world(facts["world"]) if facts["world"] else None

    with st.container(key="glass-wrapped-hero"):
        left, right = st.columns([1.4, 1], vertical_alignment="center")
        with left:
            st.image(png(art), caption="Your painting: every colour is a feeling you checked in with",
                     width="stretch")
        with right:
            st.html(
                f'<div class="wr-stat"><span>{facts["checkins"]}</span>check-ins on {facts["days"]} days</div>'
                '<div class="eyebrow" style="margin-top:1rem">Your top feelings</div>'
                + "".join(f'<div class="wr-rank"><b>{i}</b>{esc(f.capitalize())}</div>'
                          for i, f in enumerate(facts["top_feelings"], 1))
                + f'<p class="body" style="margin-top:.8rem">Overall, this period was <b>{mood_words(facts["mood"])}</b>'
                + (f'. Your brightest day was <b>{facts["brightest"]}</b>.' if facts["brightest"] else ".")
                + "</p>")

    with st.container(key="glass-wrapped-mood"):
        st.html('<div class="title-sm">Mood tracker</div>')
        st.altair_chart(mood_line(daily(table)), width="stretch")
        st.html('<div class="field-label">Feeling families</div>' + "".join(
            f'<span class="wr-chip" style="--c:{GROUP_COLOURS[f][1]}">{esc(f)} · {round(share * 100)}%</span>'
            for f, share in facts["families"] if share >= 0.03))

    with st.container(key="glass-wrapped-music"):
        st.html('<div class="title-sm">Your playlist for this period</div>')
        rows = []
        for i, track in enumerate(music.recommend(facts["emotions"][:6], "match", 0.5), 1):
            spotify, youtube = music.links(track)
            rows.append(f'<div class="track"><span class="track-num">{i:02d}</span><div><b>{esc(track["title"])}</b> · '
                        f'{esc(track["artist"])}<small>{esc(track["language"])} · {esc(track["genre"])}</small></div>'
                        f'<div class="track-links"><a href="{spotify}" target="_blank" rel="noopener">Spotify</a>'
                        f'<a href="{youtube}" target="_blank" rel="noopener">YouTube</a></div></div>')
        st.html("".join(rows))

    if world:
        with st.container(key="glass-wrapped-world"):
            st.html(f'<div class="eyebrow">The world you visited most</div>'
                    f'<div class="display" style="font-size:2rem">{esc(world["name"])}</div>'
                    f'<p class="body">{esc(world["description"])}</p>' + swatches_html(world["palette"]))

    st.download_button("Download my Wrapped card (.png)", card_png(facts, art, period, storage.get_setting("name", "")),
                       file_name="orbit_wrapped.png", mime="image/png", key="wrapped_download", type="primary")
    note("Made on this device from your journal. It shows what your check-ins say, not a diagnosis.")
