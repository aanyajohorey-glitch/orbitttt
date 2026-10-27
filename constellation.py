"""
constellation.py
The Emotion Constellation: the FULL blend of emotions in one check-in, drawn
as a star pattern.

- Every emotion the model found (above a small threshold) becomes a star.
- Stronger emotion -> bigger, brighter star. Colour = its emotion family.
- Each emotion has its own "home" direction in the sky (so joy is always in
  the same area), plus a small random shift taken from the check-in itself.
  That makes every constellation unique but still readable.
- The stars are joined in order around the centre, so they form a shape.

Only SVG (drawing with shapes) is used, so no extra libraries are needed.
Streamlit's st.html removes inline SVG for safety, so the drawing is shown
as an image (a "data:" address) with its animation CSS inside the SVG.
"""
import base64
import hashlib
import math
import random

from components import esc
from emotion_model import GO_EMOTIONS_LABELS, GROUP_COLOURS, GROUP_OF

MIN_SCORE = 0.02
MAX_STARS = 9
MIN_STARS = 3


def _seed(text):
    """The same check-in always gives the same constellation."""
    return int(hashlib.md5(str(text).encode("utf-8")).hexdigest()[:8], 16)


def stars_for(emotions, seed_text=""):
    """Work out where each star goes. Returns a list of dicts (x, y from -1 to 1)."""
    ranked = sorted(emotions, key=lambda pair: -pair[1])
    chosen = [(label, score) for label, score in ranked if score >= MIN_SCORE][:MAX_STARS]
    if len(chosen) < MIN_STARS:
        chosen = ranked[:MIN_STARS]
    strongest = max(score for _, score in chosen) or 1.0
    rng = random.Random(_seed(seed_text))
    stars = []
    for label, score in chosen:
        home = GO_EMOTIONS_LABELS.index(label) / len(GO_EMOTIONS_LABELS) * 2 * math.pi
        angle = home + rng.uniform(-0.35, 0.35)
        strength = score / strongest
        distance = 0.88 - 0.5 * strength + rng.uniform(-0.08, 0.08)
        stars.append({
            "label": label, "score": score, "strength": strength,
            "x": math.cos(angle - math.pi / 2) * distance, "y": math.sin(angle - math.pi / 2) * distance,
            "angle": angle % (2 * math.pi), "colour": GROUP_COLOURS[GROUP_OF[label]][1],
        })
    return sorted(stars, key=lambda star: star["angle"])


SVG_CSS = (
    ".cst-label{fill:#EDE8F7;font-family:system-ui,'Segoe UI',sans-serif;font-weight:500}"
    ".animate .cst-line{stroke-dasharray:100;animation:draw 1.8s ease .3s both}"
    ".animate .cst-star{transform-box:fill-box;transform-origin:center;"
    "animation:pop .7s cubic-bezier(.2,1.4,.4,1) var(--d) both}"
    ".animate .cst-label{animation:fade .6s ease var(--d) both}"
    "@keyframes draw{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}"
    "@keyframes pop{from{opacity:0;transform:scale(.2)}to{opacity:1;transform:none}}"
    "@keyframes fade{from{opacity:0}to{opacity:1}}"
    "@media (prefers-reduced-motion:reduce){.animate *{animation:none!important}}"
)


def as_image(svg, size, alt):
    """Show an SVG drawing as an image (st.html keeps images, not inline SVG)."""
    data = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return (f'<img class="cst-img" src="data:image/svg+xml;base64,{data}" width="{size}" height="{size}" '
            f'alt="{esc(alt)}">')


def constellation_svg(emotions, seed_text="", size=320, labels=True, animate=True, ink=None, uid="c"):
    """The constellation as an SVG drawing.

    With labels (the big version) it sits on a round night sky. ink: one colour
    for every line and star (used on planets, which have no sky).
    """
    stars = stars_for(emotions, seed_text)
    half = size / 2
    pad = 0.64 if labels else 0.84

    def point(star):
        return half + star["x"] * half * pad, half + star["y"] * half * pad

    points = [point(star) for star in stars]
    path = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(points)) + " Z"
    scale = size / 320
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" class="constellation{" animate" if animate else ""}" '
        f'viewBox="0 0 {size} {size}" width="{size}" height="{size}">',
        f"<style>{SVG_CSS}</style>",
        f'<defs><filter id="glow-{uid}" x="-80%" y="-80%" width="260%" height="260%">'
        f'<feGaussianBlur stdDeviation="{3 * scale:.1f}"/></filter>'
        f'<radialGradient id="sky-{uid}" cx="45%" cy="40%" r="65%"><stop offset="0" stop-color="#4A4170"/>'
        f'<stop offset="1" stop-color="#25213A"/></radialGradient></defs>',
    ]
    if labels:
        parts.append(f'<circle cx="{half}" cy="{half}" r="{half - 1}" fill="url(#sky-{uid})"/>')
        dust = random.Random(_seed(seed_text) + 7)
        for _ in range(38):
            angle, distance = dust.uniform(0, 2 * math.pi), half * 0.93 * math.sqrt(dust.random())
            parts.append(f'<circle cx="{half + math.cos(angle) * distance:.1f}" cy="{half + math.sin(angle) * distance:.1f}" '
                         f'r="{dust.uniform(0.4, 1.1) * scale:.1f}" fill="#fff" opacity="{dust.uniform(0.15, 0.5):.2f}"/>')
    line_colour = ink or "#E8E2F7"
    parts.append(f'<path class="cst-line" d="{path}" fill="none" stroke="{line_colour}" stroke-opacity="0.5" '
                 f'stroke-width="{max(1.0, 1.3 * scale):.1f}" stroke-linejoin="round" pathLength="100"/>')
    placed = []
    for i, (star, (x, y)) in enumerate(zip(stars, points)):
        radius = (2.5 + 10 * math.sqrt(star["score"])) * scale
        colour = ink or GROUP_COLOURS[GROUP_OF[star["label"]]][0]
        opacity = 0.55 + 0.45 * star["strength"]
        parts.append(
            f'<g class="cst-star" style="--d:{0.15 * i + 0.4:.2f}s">'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius * 2.3:.1f}" fill="{colour}" '
            f'opacity="{opacity * 0.6:.2f}" filter="url(#glow-{uid})"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{colour}" opacity="{opacity:.2f}"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius * 0.45:.1f}" fill="#fff" opacity="0.95"/></g>'
        )
        if labels and star["score"] >= 0.04:
            anchor = "start" if x >= half else "end"
            text_width = (len(star["label"]) + 4) * 6.2 * scale
            if anchor == "end" and x - radius - 6 - text_width < 2:
                anchor = "start"
            elif anchor == "start" and x + radius + 6 + text_width > size - 2:
                anchor = "end"
            dx = radius + 6 if anchor == "start" else -(radius + 6)
            label_y = y + 4
            while any(abs(label_y - other_y) < 13 * scale and abs(x - other_x) < 90 * scale
                      for other_x, other_y in placed):
                label_y += 13 * scale
            placed.append((x, label_y))
            parts.append(
                f'<text class="cst-label" style="--d:{0.15 * i + 0.6:.2f}s" x="{x + dx:.1f}" y="{label_y:.1f}" '
                f'text-anchor="{anchor}" font-size="{11 * scale:.1f}">{esc(star["label"])} '
                f'{star["score"]:.0%}</text>'
            )
    parts.append("</svg>")
    return "".join(parts)


def constellation_html(emotions, seed_text="", size=320, labels=True, animate=True):
    """The constellation, ready to place in st.html."""
    svg = constellation_svg(emotions, seed_text, size=size, labels=labels, animate=animate)
    return as_image(svg, size, "Emotion constellation. " + describe(emotions))


def constellation_planet(emotions, primary, seed_text="", size=80, uid="p"):
    """A planet with its check-in's constellation drawn across it (for the galaxy)."""
    light, dark = GROUP_COLOURS[GROUP_OF[primary]]
    svg = constellation_svg(emotions, seed_text, size=size, labels=False, animate=False, ink="#FFFFFF", uid=uid)
    inner = as_image(svg, size, "")
    return (f'<div class="planet cst-planet" style="--c1:{light};--c2:{dark};--size:{size}px">'
            f'<div class="sphere"></div><div class="cst-overlay">{inner}</div></div>')


def describe(emotions):
    """A short sentence for screen readers and the viva: what the shape shows."""
    stars = stars_for(emotions)
    names = [star["label"] for star in sorted(stars, key=lambda s: -s["score"])[:3]]
    return (f"{len(stars)} stars. Brightest: " + ", ".join(names) + ". "
            "Bigger, brighter stars are stronger emotions.")
