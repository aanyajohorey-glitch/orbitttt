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

`data/creative_profiles.csv` has 31 styles, written for ORBIT (you can open it in Excel). Each row
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

- The **style table** (31 styles, their keywords, colours, tags and "avoid" lists) was written for ORBIT
  and linked to ORBIT's own aesthetics, fonts, music and creator data.
- The **scoring rules** (phrase 3 / word 2 / related 1; +1.0 / +0.6 / +0.4 / −0.5; 60/40 blend; 0.3 bar)
  were designed and tuned for this project and tested on seven ideas.
- The **"phrase first, words are used up"** rule solves the "dark" problem.
- It uses simple Python only: no neural network, no new trained model, no paid API.

## 9. Limits (honest)

- It only knows the 31 styles in the table. New styles must be added as new rows.
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
