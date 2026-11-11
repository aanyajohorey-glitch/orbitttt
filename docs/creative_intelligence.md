# The ORBIT Creative Feature Matching Algorithm

A guide for explaining ORBIT's Create Mode recommender in the viva.

## 1. What it does

When you type a creative idea, for example **"Dark Romance"**, the algorithm:

1. finds the important keywords in the idea,
2. matches them to creative **styles** that ORBIT knows (Dark Romance, Cottagecore, Cyberpunk, ...),
3. gives every resource (aesthetic, font, song, creator) a **score** for how well it fits those styles, and
4. recommends the resources with the highest scores.

It also gives the palette the style's colour and helps pick a font that suits the style.

## 2. Why it was introduced

Before, Create Mode worked out everything from **emotions** and a few mood words. That works for
"a rainy Sunday café, nostalgic and warm", but not for style names:

| Idea | Words ORBIT understood before | Top aesthetics before |
|---|---|---|
| Dark Romance | only "dark" | Film Noir, **Cyberpunk**, Dark Academia |
| Dark Academia | only "dark" | exactly the same as Dark Romance |
| Cottagecore, Cyberpunk, Minimalist Luxury, Ethereal Fantasy | nothing | Pastel Goth, French New Wave, Surrealism (the same for all four) |

The emotion model reads a two-word idea like "Cyberpunk" as *neutral*, so the results fell back to the
middle. And the word "dark" only made things darker, so Dark Romance could get horror-like or random sad
results. The new algorithm fixes this by understanding **creative styles**, not just feelings.

## 3. The knowledge table

`data/creative_profiles.csv` has 41 styles (31 at first), written for ORBIT (you can open it in Excel). Each row
describes one style:

| Column | Dark Romance (example) |
|---|---|
| phrases | dark romance, gothic romance, forbidden love, vampire romance |
| words / related | (other styles use these, e.g. Cottagecore: "cottagecore" / "garden, baking") |
| atmosphere | mysterious, dramatic, passionate |
| colours | burgundy, deep red, charcoal, antique gold |
| aesthetics | Gothic, Pre-Raphaelite, Baroque |
| tags | romantic, dark, dramatic, mystery, ornate, longing, ... |
| font_tags | elegant, romantic, dramatic, classic, literary |
| music_tags / music_genres | love, longing, night, classical · Modern classical, Soul, Jazz, Ghazal, Sufi |
| avoid | playful, cute, celebration, dance, fun, grief, sunny, ... |
| hue, harmony | 345 (burgundy-rose), analogous (neighbouring reds) |
| mood, energy, light, warmth, era, texture, bold | numbers from -1 to +1 |

Every aesthetic, genre and tag in the table really exists in ORBIT's other data files (a test checks this).

## 4. How it works, step by step

**Step 1: Find keywords.** ORBIT looks for whole **phrases first** (3 points), then single **words**
(2 points), then **related words** (1 point). A word used inside a phrase is "used up". So in
"Dark Romance", "dark" is part of the phrase and is **not** counted again on its own. That is why
Dark Romance does not turn into horror.

**Step 2: Match styles.** Each style adds up its points. Its **strength** = its points ÷ the best
style's points. Styles with strength 0.5 or more are kept (at most two). "Dreamy Nostalgia" gives
Dreamy 2 points and Nostalgia 2 points, so both are kept with strength 1.0 and blended equally.

**Step 3: Score every resource (the idea match, from -0.5 to 1).** For each kept style:

| Rule | Points |
|---|---|
| The style names this aesthetic | +1.0 |
| Shared tags | +0.6 × (shared tags ÷ the item's tags) |
| The song's genre is one the style lists | +0.4 |
| The item has a tag the style avoids | −0.5 |

The total is kept between −0.5 and 1. With two styles, the scores are averaged by strength.

**Step 4: Combine and recommend.**

> **final score = 60% idea match + 40% ORBIT's existing score**

The existing score is the one ORBIT already had (closeness to the Vibe Vector plus shared words), so
the feeling of the idea still counts. Only resources that clearly fit (idea match 0.3 or more) compete
for the places, then the existing variety rule (MMR) picks a varied set among them.

**The style also shapes the look:**
- **Colour:** the style's hue replaces the emotion-based hue; the harmony rule (e.g. analogous) comes
  from the style; saturation and lightness are averaged 50/50; the accessibility (WCAG) checks still run.
- **Fonts:** a font whose tags fit the style gets a head start: its distance is reduced by 3 × its idea
  match (half of that for body text, which must stay readable).
- **Numbers:** the style's light, warmth, era, texture, boldness, mood and energy are averaged 50/50
  with the numbers ORBIT worked out before.

If an idea names **no** style (for example "a dark night poster"), nothing changes: Create Mode works
exactly as before.

## 5. A worked example: "Dark Romance"

1. Keywords: the phrase "dark romance" is found → **Dark Romance: 3 points, strength 1.0**.
2. Gothic (tags: dark, dramatic, cathedral, mystery):
   named by the style +1.0, shared tags 3 of 4 → +0.6 × 0.75 = +0.45. Total 1.45, kept at **1.0**.
3. Cyberpunk (tags: neon, dystopian, tech, urban): not named, no shared tags → **0.0**.
   It cannot compete, because it is below 0.3.
4. A love ghazal (tags: love, longing, calm; genre Ghazal): shared 2 of 3 → +0.4, genre +0.4 = **0.8**.
   A party song (tags: dance, celebration) has avoided tags → **−0.5**, so it drops down.
5. Final score for Gothic = 0.6 × 1.0 + 0.4 × (its existing score). It comes first.

**Result:** Gothic and Pre-Raphaelite aesthetics, a rose-burgundy palette with deep burgundy-charcoal
ink, Playfair Display (tagged elegant, classic), love and longing songs such as a Sufi song, a ghazal
and Clair de Lune, and creators like Tim Burton and Raja Ravi Varma.

## 6. Results for the seven test ideas

| Idea | Top aesthetics | Palette | Heading font | Music feel |
|---|---|---|---|---|
| Dark Romance | Gothic, Pre-Raphaelite, Film Noir | rose / burgundy | Playfair Display | love, longing, classical, ghazal |
| Dark Academia | Dark Academia, Gothic, Pre-Raphaelite | warm browns / coral | Crimson Pro | jazz, Hindustani and Western classical |
| Cottagecore | Cottagecore, Studio Ghibli-esque, Scandinavian Hygge | sage greens | Dancing Script | acoustic, indie folk |
| Cyberpunk | Cyberpunk, Glitch Art, Synthwave | neon orchid + mint | Orbitron | synth pop, electronic, hip hop |
| Dreamy Nostalgia | Impressionism, Surrealism, Lo-fi Anime | lavender | Libre Baskerville | dream pop, old Hindi film songs |
| Minimalist Luxury | Minimalism, Swiss Style, Art Deco / Japandi | soft neutrals | Raleway | modern classical, ambient, jazz |
| Ethereal Fantasy | Art Nouveau, Pre-Raphaelite, Studio Ghibli-esque | periwinkle / lavender | elegant serif or sans | new age, ambient, modern classical |

These are checked by automatic tests in `tests/test_creative_match.py`. Results can differ a little with
the real emotion model, because the existing 40% part still depends on the feeling.

## 7. How it improves ORBIT

- Recommendations now follow the **creative direction** of the idea, not only its emotion.
- Similar-sounding ideas (Dark Romance vs Dark Academia) now get **different**, fitting results.
- The word "dark" no longer pulls in horror or random sad songs when it is part of a style.
- Every choice can be **explained**: the "why" lines say what matched ("Fits your idea: dark, dramatic"),
  the concept card says "ORBIT read your idea as: Dark Romance", and *How this was made* shows the points.
- Nothing was removed: the emotion model and Feel Mode are unchanged.

## 8. What makes it our own component

- The **style table** (41 styles, their keywords, colours, tags and "avoid" lists) was written for ORBIT
  and linked to ORBIT's own aesthetics, fonts, music and creator data.
- The **scoring rules** (phrase 3 / word 2 / related 1; +1.0 / +0.6 / +0.4 / −0.5; 60/40 blend; 0.3 bar)
  were designed and tuned for this project and tested on seven ideas.
- The **"phrase first, words are used up"** rule solves the "dark" problem.
- It uses simple Python only: no neural network, no new trained model, no paid API.

## 9. Limits (honest)

- It only knows the 41 styles in the table. New styles must be added as new rows.
- Keywords must be spelled as in the table (simple plurals like "dreams" are understood).
- The numbers (60/40, 0.3, +1.0, ...) are design choices, not learned from data. A small user study
  (rating fit 1-5 before and after) would show how much it really helps.

## 10. Where the code is

| File | What it does |
|---|---|
| `data/creative_profiles.csv` | the style table |
| `creative_match.py` | Steps 1-4: keywords, styles, item scores, the 60/40 blend |
| `vibe.py` | attaches the matched styles to the Vibe Vector and averages their numbers |
| `creative.py` | uses the idea match for aesthetics, creators and music; passes colour and fonts on |
| `palette.py`, `fonts.py`, `music.py` | style colour, font head start, music idea score |
| `create_ui.py` | "ORBIT read your idea as ..." and the explanation in *How this was made* |
| `tests/test_creative_match.py` | 17 tests, including the seven ideas |

---

# Part 2: The Creative Brief, colour stories, patterns and free online sources

## 11. The whole workflow

```
Idea → crisis check (unchanged: a crisis idea gets only helplines, nothing is generated or sent)
  1. ORBIT Creative Brief Builder (our own, no AI service)   → genre, aesthetic, atmosphere, emotion,
                                                               colours, patterns, typography, music
  2. ORBIT colour story palette (no API)                     → Primary, Secondary, Accent, Background, Text
  3. Search free sources: typed idea (cleaned) + brief phrases → Unsplash, Openverse, Pixabay (images)
                                                               Last.fm + MusicBrainz (songs)
                                                               Google Fonts (fonts)
  4. ORBIT scores every result (simple points, below)
  5. Filter: low scores, "avoid" words, repeats, one per photographer or artist
  6. Show the creative world, with credits and licences
```

We decided **not** to use Gemini: its terms do not allow apps used by people under 18, and ORBIT is
for school students. So the "understanding" step is ORBIT's own Creative Brief Builder.

## 12. The Creative Brief Builder

The style table now has **41 styles** (for example Dark Romance, Gothic Romance, Dark Fantasy, Gothic
Architecture, Fairycore, Royalcore, Witchy, Autumn Cosy, Old Hollywood, Lo-fi, Coastal). Each row also
holds the brief: genre, emotional direction, typography personality, music character, 6-7 **named
colours**, 3-4 **patterns**, 3-4 **image search phrases**, words to **avoid** in images, and **Last.fm
tags**. Phrases are matched first, so "Gothic Romance", "Dark Romance", "Dark Fantasy", "Gothic
Architecture" and plain "Gothic" are all different styles.

## 13. Colour stories (the palette fix)

Before, every palette came from one hue and the main colour was forced to stay light, so Dark Romance
got rose, orchid and coral. Now each style has a named colour story, e.g. Dark Romance:
Deep Burgundy, Wine Red, Muted Rose, Dusty Mauve, Deep Plum, Antique Ivory, Charcoal.

1. **Dark style** (its light number is below -0.25): the **darkest** colour is the background and the
   **lightest** is the text. A light style does the opposite.
2. The other colours, in the order the style lists them, become **Primary, Secondary, Accent**.
   With two styles, colours are taken in turns, so both styles show.
3. Small nudges keep the refine buttons working: warmer or cooler hues, lighter or darker, more or less
   saturated. The style's character stays.
4. The text colour is moved until **text on the background passes WCAG AA (4.5 : 1)**.

## 14. Patterns and textures

Each style lists its own patterns (Dark Romance: damask, rose motif, velvet, candle glow; Cottagecore:
gingham, wildflower sprigs, embroidery, linen; Cyberpunk: neon grid, circuit lines, scanlines). ORBIT
draws them in the palette's own colours (`pattern_swatches.py`, 61 patterns). Ideas with no style keep
the old textures.

## 15. Moodboard images: the scoring

The cleaned typed idea (first) and the brief's search phrases (e.g. "red roses candlelight",
"burgundy velvet") are sent to Unsplash,
Openverse and Pixabay. Every image gets:

| Rule | Points |
|---|---|
| Brief words found in its title and tags | +0.6 × (words found ÷ 3, at most 1) |
| Its main colour is close to the palette (Unsplash gives this) | +0.3 × closeness (half marks if unknown) |
| It came from an on-brief search | +0.1 |
| It contains a word the style avoids, or a vehicle, logo, screenshot or 3D avatar | −0.5 |

Kept if the score is **0.5 or more**. Then: at most **one image per photographer**, at most **3 per
search**, no repeated titles, and the searches take turns so the board is varied. Every image shows its
photographer, source and licence, and links to its page.

## 16. Music and fonts from online sources

**Songs.** ORBIT's own 271-song playlist stays first. Below it, *More to discover* comes from Last.fm
songs with the brief's tags (e.g. "romantic", "dark pop"). Each gets:
+0.6 × (brief tags it appears under ÷ tags searched), +0.4 if MusicBrainz confirms the song and one of
its genre tags fits the style, −0.5 for avoided words. Kept at 0.3 or more, one per artist, and never a
repeat of ORBIT's own playlist.

**Fonts.** ORBIT's list grew from 77 to **97** tagged fonts (blackletter, medieval, Victorian, formal
scripts). Google Fonts adds popular families in the categories the style needs (serif, display,
handwriting, ...): score = 0.6 × category fit + 0.4 × popularity.

## 17. Free use, limits and what happens when a service is unavailable

| Source | Key | Free limit | ORBIT's rule |
|---|---|---|---|
| Unsplash | free Access Key | 50 requests/hour (demo) | budget 40/hour, credit photographer + Unsplash, images shown from Unsplash's links |
| Pixabay | free key | 100 requests/minute | searches kept 24 hours (Pixabay asks for this), shown only as search results |
| Openverse | none (optional free registration) | 20/minute, 200/day without a key | licence and credit on every image, photographs only |
| Last.fm | free key | "reasonable use", non-commercial | budget 60/minute, credit Last.fm |
| MusicBrainz | none | 1 request/second | waits 1.1 s between checks, named User-Agent |
| Google Fonts | free key | normal Google Cloud quota, no billing | the list is kept for 24 hours |

- Every search is remembered for 24 hours, so repeating an idea costs nothing.
- If a key is missing, a limit is reached or a service is down, that source is skipped and a small line
  says so ("Unsplash: not set up"). If no image source works, the moodboard falls back to ORBIT's own
  tiles; music always has ORBIT's playlist; fonts always have ORBIT's list. Create Mode never crashes.
- **Privacy:** image searches use ORBIT's own phrases plus, as the first search, the idea the user typed
  in Create, cleaned by `safe_query()`: emails, web links and numbers of 5 or more digits are removed and
  only the first 8 words are kept. The typed words are never sent for a crisis or concern message, in
  offline demo mode, from the Feel → Create bridge (check-in text), or to Last.fm, MusicBrainz or Google
  Fonts. Nothing at all is sent after a crisis check, in offline demo mode, or when *Settings → Online
  images, music and fonts* is off.
- **Safety:** Unsplash content filter "high", Pixabay safe search, Openverse "mature" off.

## 18. Before and after (8 test ideas)

| Idea | Palette before | Palette now | Patterns now | Heading font now |
|---|---|---|---|---|
| Dark Romance | Soft Rose, Soft Orchid, Soft Coral | Deep Burgundy, Wine Red, Muted Rose on Charcoal | damask, rose motif, velvet, candle glow | Spectral SC |
| Dark Academia | Soft Coral, Soft Rose, Soft Honey | Oxblood, Walnut Brown, Forest Green on Ink Black | tweed, old paper, leather, ink blots | Crimson Pro |
| Dark Fantasy | Soft Mint, Soft Berry (read as plain "Fantasy") | Deep Forest, Obsidian, Ember Red on Shadow | celtic knots, runes, stone texture | Grenze Gotisch |
| Cottagecore | Soft Sage, Pale Lime | Sage Green, Wildflower Pink, Honey on Cream Linen | gingham, wildflower sprigs, embroidery, linen | Dancing Script |
| Cyberpunk | Vivid Orchid, Soft Honey, Soft Mint | Neon Magenta, Electric Cyan, Acid Yellow on Night Black | neon grid, circuit lines, scanlines, glitch bands | Orbitron |
| Dreamy Nostalgia | Dusty Lavender, Pale Lavender | Lavender Haze, Faded Orange, Baby Blue on Cloud White | clouds, watercolour wash, film grain | Cormorant |
| Minimalist Luxury | Soft Apricot, Soft Rose | Stone Grey, Champagne Gold, Warm Taupe on Ivory | fine grid, linen, marble | Raleway |
| Ethereal Fantasy | Soft Periwinkle, Pale Sky | Pearl Lilac, Emerald, Moon Silver on Pearl White | clouds, pearls, watercolour wash | Marcellus |

Before, every idea had the same three textures (soft grain, linen, film grain) and the moodboard had no
images. Now the textures follow the style and the moodboard shows real, credited images. Image and
online-song quality depends on which keys are set up (see `.streamlit/secrets.toml.example`).

## 19. Where the new code is

| File | What it does |
|---|---|
| `data/creative_profiles.csv` | 41 styles with their full brief (colours, patterns, searches, tags) |
| `creative_match.py` | `brief()`, `anchors()`, `image_keywords()` added to the matching algorithm |
| `palette.py` | `anchor_palette()`: the colour story palette |
| `pattern_swatches.py` | 61 patterns drawn in the palette's colours |
| `online_sources.py` | the six free services, budgets, 24-hour memory, scoring and filtering |
| `create_ui.py` | the Creative Brief card, image moodboard, colour story, "More to discover", sources line |
| `tests/test_online_sources.py` | tests with saved sample answers (no internet, no quota used) |

