"""
brief.py
Creator Mode export: a one-page creative brief as a PDF.

Drawn with Pillow (already installed with Streamlit), so no extra library is
needed: the page is drawn as an A4 image and saved as a PDF.
"""
import io
import textwrap
import unicodedata

from PIL import Image, ImageDraw, ImageFont

from palette import hex_to_rgb

WIDTH, HEIGHT, MARGIN = 1240, 1754, 90          # A4 at 150 dots per inch
INK = (52, 49, 59)
MUTED = (110, 104, 118)


# Fonts with accented letters (and Devanagari, for Nirmala UI on Windows). Tried in order.
SYSTEM_FONTS = ["Nirmala.ttc", "Nirmala.ttf", "DejaVuSans.ttf", "arial.ttf", "Arial.ttf"]
_FULL_FONT = None


def _font(size):
    global _FULL_FONT
    for name in SYSTEM_FONTS:
        try:
            font = ImageFont.truetype(name, size)
            _FULL_FONT = True
            return font
        except OSError:
            continue
    _FULL_FONT = False
    try:
        return ImageFont.load_default(size=size)
    except TypeError:            # very old Pillow
        return ImageFont.load_default()


def _safe(text):
    """Pillow's built-in font has no accents: turn 'été' into 'ete' rather than empty boxes."""
    if _FULL_FONT:
        return text
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def _wrapped(draw, xy, text, font, width_chars, fill=INK, gap=8):
    x, y = xy
    for line in textwrap.wrap(_safe(text), width_chars):
        draw.text((x, y), line, fill=fill, font=font)
        y += font.size + gap
    return y


def page_image(universe):
    """The brief drawn as one A4 page (a Pillow image)."""
    page = Image.new("RGB", (WIDTH, HEIGHT), (250, 248, 244))
    draw = ImageDraw.Draw(page)
    h1, h2, body, small = _font(52), _font(26), _font(22), _font(18)
    concept, colours = universe["concept"], universe["palette"]["colours"]
    vector = universe["vector"]

    # gradient band at the top (primary -> harmony A)
    a, b = hex_to_rgb(colours[0]["hex"]), hex_to_rgb(colours[1]["hex"])
    for x in range(WIDTH):
        t = x / WIDTH
        draw.line([(x, 0), (x, 26)], fill=tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)))

    y = 70
    draw.text((MARGIN, y), "CREATIVE BRIEF · ORBIT CREATOR MODE", fill=MUTED, font=small)
    y += 40
    y = _wrapped(draw, (MARGIN, y), concept["title"], h1, 34, gap=10) + 10
    if vector.get("direction"):
        draw.text((MARGIN, y), f"Direction: {vector['direction']}", fill=MUTED, font=small)
        y += 34
    y = _wrapped(draw, (MARGIN, y), concept["vision"], body, 88) + 30

    # palette
    draw.text((MARGIN, y), "PALETTE", fill=MUTED, font=small)
    y += 32
    swatch = (WIDTH - 2 * MARGIN - 4 * 20) // 5
    for i, colour in enumerate(colours):
        x = MARGIN + i * (swatch + 20)
        draw.rounded_rectangle([x, y, x + swatch, y + 130], radius=16, fill=colour["hex"], outline=(220, 216, 226))
        draw.text((x, y + 142), _safe(colour["name"]), fill=INK, font=small)
        draw.text((x, y + 166), f"{colour['hex']} · {colour['role']}", fill=MUTED, font=small)
    y += 220
    draw.text((MARGIN, y), f"Harmony rule: {universe['palette']['rule']}. Text contrast: " + ", ".join(
        f"{c['pair']} {c['ratio']}:1" for c in universe["palette"]["checks"][:2]), fill=MUTED, font=small)
    y += 50

    def section(title, lines, wrap=90):
        nonlocal y
        draw.text((MARGIN, y), title.upper(), fill=MUTED, font=small)
        y += 30
        for line in lines:
            y = _wrapped(draw, (MARGIN, y), line, body, wrap, gap=6) + 6
        y += 22

    fonts = universe["fonts"]
    section("Typography", [f"{fonts['heading']} for headings, {fonts['body']} for text (Google Fonts, open licence)."])
    mood = universe["moodboard"]
    section("Moodboard", [f"Lighting: {mood['lighting']}. Textures: {', '.join(mood['textures'])}.",
                          "Keywords: " + ", ".join(mood["keywords"])])
    section("Aesthetics", [f"{a['name']} ({a['era_label']}): {a['why']}" for a in universe["aesthetics"]])
    section("Music to work to", ["; ".join(f"{t['title']} by {t['artist']}" for t in universe["music"][:6])])
    section("Creators to look up", [f"{c['name']}, {c['field']}: {c['known_for']}" for c in universe["creators"][:5]])

    draw.text((MARGIN, HEIGHT - 70), "Made with ORBIT Creator Mode. Generated visuals only; music and creators are "
              "suggestions to look up, not copied work.", fill=MUTED, font=small)
    return page


def pdf(universe):
    """Returns the brief as PDF bytes."""
    buffer = io.BytesIO()
    page_image(universe).save(buffer, format="PDF", resolution=150)
    return buffer.getvalue()
