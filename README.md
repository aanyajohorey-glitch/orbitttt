# ORBIT

*Every feeling has a universe.*

**ORBIT is a companion for creative people: it helps you feel okay and helps you make things.**
Built for a Class 12 CBSE Artificial Intelligence project, it has two modes:

- **Create:** type or say an idea (or nothing at all) in English, Hinglish or Hindi, and ORBIT builds
  a cohesive *creative universe*: concept, palette, typography, moodboard, aesthetics, music and
  creators to discover, all from one explainable **Vibe Vector**.
- **Feel:** check in with how you feel. ORBIT detects the emotions, replies like a caring listener,
  keeps you safe, suggests a coping exercise or a stress-buster game, and helps you reach out to people.

**Problem statement.** Creative people struggle to turn raw ideas, emotions and abstract concepts
into a clear, cohesive creative direction: it takes repeated prompting and many platforms to find
palettes, moodboards, typography, references, music and artists, and discovering unfamiliar artists
and genres is hard. Creative work is also emotionally demanding, and many creators have no one to
talk to. ORBIT interprets ideas and emotions to produce cohesive creative concepts, and supports
wellbeing with safe, explainable check-ins, coping tools and stress-buster games.

Built with **Python**, **Streamlit**, **pandas**, **Altair**, **SQLite**
and a **pre-trained transformer model** running offline.

> Create (Creator Mode) and Feel (wellbeing) modes, joined by two bridges.
> ORBIT has its own trained classifier, confidence handling, "Teach Orbit", a tested safety net that
> runs first in both modes, 458 automated tests and CI.
>
> Documentation: [methodology](docs/methodology.md) · [safety report](docs/safety_report.md) ·
> [model card](docs/model_card.md) · [data card](docs/data_card.md) · [viva Q&A](docs/viva_qa.md) ·
> [3-minute demo script](docs/demo_script.md) · [deployment](docs/deploy.md)

## The 4Ws

| | |
|---|---|
| **Who** has the problem? | Teenagers and young creators in India (students who make posters, films, music, writing, brands), often writing in English, Hinglish or Hindi, many without easy access to a mentor or counsellor. |
| **What** is the problem? | Turning a raw idea or feeling into a cohesive creative direction takes many tools and much trial and error, and unfamiliar artists and genres are hard to discover. Creative work is also emotionally demanding, with blocks, comparison, burnout and exam stress, and many have no one to talk to. |
| **Where** does it happen? | At home and at school, on a phone or laptop, often offline or on weak internet, and inside the creative process itself (the moment of being stuck). |
| **Why** does it matter? | Creative confidence and mental wellbeing affect learning, future work and health. A free, private, explainable tool that supports both can reach people other services don't. |

## Objectives

1. Turn an idea (or nothing at all, via Spark) into a **cohesive creative universe** from one explainable
   Vibe Vector: concept, palette with WCAG checks, fonts, moodboard, aesthetics, music and creators.
2. Help users **discover beyond the mainstream**, including Indian indie, regional, folk and classical
   artists, with a measurable discovery dial.
3. Read feelings in **English, Hinglish and Hindi** with calibrated confidence, and **ask** when unsure.
4. Keep users **safe**: deterministic crisis handling first, in both modes, with helplines; no diagnosis.
5. Offer **evidence-based coping tools**, stress-buster games, Reach Out drafts, letters and a safety plan,
   and gently point to real people.
6. Keep data **private** (on the device, exportable) and **evaluate honestly**.

## SDGs

| SDG | Target | The feature that serves it |
|---|---|---|
| **SDG 3: Good Health and Well-being** (primary) | 3.4: promote mental health and well-being | Feel mode: check-ins, coping tools, stress-buster games, Reach Out Helper, Safety Plan, dependence nudges, crisis safety net with Tele-MANAS |
| **SDG 8: Decent Work and Economic Growth** | 8.3: support creativity, innovation and small enterprises | Create mode turns ideas into professional-style creative briefs (palette, type, references) for young creators and small brands, for free |
| **SDG 9: Industry, Innovation and Infrastructure** | 9.5: enhance research and technological capability | Explainable, offline-first AI (Vibe Vector, cosine similarity + MMR, occlusion heatmap) with an open evaluation lab |
| **SDG 10: Reduced Inequalities** | 10.2: social and economic inclusion of all | Free and offline; Hinglish and Hindi; Indian regional, folk and classical creators in discovery |
| SDG 4: Quality Education (optional) | 4.7: knowledge and skills | Exam-stress support, emotional vocabulary, CBT thought reframe, and the evaluation as a learning tool |

## How ORBIT is organised

Every visit opens on a **landing page**: a small universe with planets revolving around a glowing
core, and a card that asks your **name and age** (saved only on this device). One line reminds you
that ORBIT is an AI, not a therapist, with the helplines. **Start Exploring Your Universe** opens the
app at the mode you used last. There are three tabs:

| Tab | Sections | What it does |
|---|---|---|
| **Create** | Creative universe | **Creator Mode**: one idea → concept, palette, type, moodboard, aesthetics, music, creators; refine chips, sliders, locks, three directions (Safe, Bold, Weird), version history, PDF brief. "I don't have an idea yet" opens the **Spark** path. |
| | Quick palette & music | The Mood Studio: a palette or playlist straight from a feeling or a vibe. |
| **Feel** | Check-in | A guided flow: **1** check in (text) → **2** what ORBIT noticed (emotion + confidence) → **3** ORBIT's reply → **4** one small exercise to try → **5** mood after → **6** a new planet joins your galaxy. |
| | Talk to ORBIT | A chat. Every message is checked for safety first, then analysed; replies reflect, validate and ask one gentle question. |
| **My Galaxy** | Galaxy & journal | Private mood history: emotional weather, patterns, insights and a **galaxy where every check-in is a planet**. |
| | Wrapped | **ORBIT Wrapped**, like a year-in-review: for 7 days, 30 days, a year or all time, your top feelings, a mood tracker, an **abstract painting made from your emotion blend**, a playlist for the period, the world you visited most, and a card to download. |
| | Patterns | **Pattern Insights** over 7 days, 14 days, 30 days or a year: feelings, mood line, calendar heatmap, when low moods cluster, and layered suggestions. |
| | Saved worlds · Collection | Saved aesthetic worlds, as planets on an orbit, and as a collection. |
| | Calm Room | Breathing (box, 4-6, 4-7-8), 5-4-3-2-1 grounding, a **CBT thought reframe** and a gratitude jar, with mood before and after. |
| | Mood Lab | Detailed analysis with **"Why does ORBIT think this?"** (word importance), and Hinglish translation. |
| | Soundspace | Soundscapes generated by Python maths. |
| | Stress busters | Nine gentle 2-5 minute games (no scores). Also offered once per visit after a confident stress, anxiety, sadness or anger check-in, never for happy/neutral feelings, a crisis or repeated low moods. |
| | Reach Out | **Reach Out Helper**: drafts a short message to a friend, parent or teacher that you edit, copy and send yourself. |
| | Letters | **A letter you'll never send** (let it burn or float away; nothing kept unless you choose) and **a letter to future me** (sealed for 30 days, then shown next to what you felt). |
| | Safety plan | Your own plan for hard moments: warning signs, what helps, people and helplines. Private. |
| | Arcade | A realistic vending machine; tokens are **earned by self-care**. |

Also on every page: the **Settings** menu (top right) with high contrast, dark theme, larger
text, the readability font, reduce motion, background music, who writes replies, demo mode, and
**download / import my data**; and **thumbs up/down** under replies and exercises. After a long session, or several low-mood
check-ins in a week, ORBIT gently suggests **talking to a real person**.

In **Today**, step 2 shows the check-in's **emotion constellation** (every detected emotion is a
star; stronger = bigger and brighter) and the words that drove the decision glowing brighter. Each
check-in's constellation becomes a planet in the galaxy. After a feeling is detected, the **whole app
takes on that feeling's world** (colours from `worlds.csv`, smooth fade).

**Background music:** a calm general soundscape plays from the moment you press Start (that tap is
what browsers need before they allow sound). Once ORBIT knows your mood, or you build a creative
universe, it changes to that world's soundscape. It pauses while a Soundspace track plays, and can be
switched off in Settings.

**Accessibility (Settings, top right):** reduce motion (also follows the device setting), larger text,
high contrast, a dark theme and the Lexend readability font.

**Offline demo mode** (Settings, or automatic if the model can't load): sample sentences
give real results saved earlier; other text gets a simpler text-only estimate (variant T,
out-of-fold accuracy 0.45). Safety checks work exactly as usual.

Every result in Today, Mood Lab and the chat shows **how sure ORBIT is**. When it isn't sure, or
the message is very short or vague, it **asks a gentle clarifying question** instead of naming a
feeling. Under every result, **"Not quite right? Teach ORBIT"** lets the user pick a better feeling;
corrections stay on the computer and can be used to retrain the classifier.

## Creator Mode (the Create tab)

**Entry.** One big box: *"What are you making, or what's on your mind?"* (English, Hinglish or Hindi), with optional tap-chips for medium, audience and "start from a feeling, colour,
song or word". The **crisis check runs first, silently**: crisis wording shows only the helplines,
nothing is generated and the text is not kept. If something is unclear, ORBIT asks **at most three
tappable questions** (medium, feeling, era), which can all be skipped.

**The Vibe Vector (`vibe.py`).** One set of numbers describes the idea: the emotion blend (from
ORBIT's emotion model, with the "why" heatmap), **valence, arousal, brightness, warmth, era, texture,
boldness** and **themes**. Small, readable word tables turn words like *rainy*, *nostalgic*, *neon*
or *grandmother* into those numbers; Hinglish and Hindi ideas are matched through their English
translation. **Every output is generated from this one vector**, which is why the results fit together.

**The Creative Universe (`creative.py`).**

| Output | Method |
|---|---|
| Concept | Title + one-paragraph vision from a template grammar. Optional **AI polish** (cloud or local, only if set up) with the template as fallback and the same output checks as replies. |
| Palette | 5 colours with names, roles, hex codes and a WCAG contrast check (`palette.py`): valence and arousal → hue, saturation and lightness, plus a harmony rule. |
| Typography | Closest heading font in `data/fonts.csv` (77 Google Fonts tagged by mood), plus a readable body font from a different family; Devanagari fonts for Hindi ideas. Every font is **shown in its own typeface**, with eight more font ideas for the vibe (at most two per category, for variety). |
| Moodboard | Generated gradients, patterns, lighting and keyword tiles; no images. |
| Aesthetics | The 3 closest of 66 movements in `data/aesthetics.csv` (Bauhaus to Madhubani to Solarpunk). |
| Music | 8 tracks from `data/music_catalog.csv` with Spotify/YouTube search links. |
| Creators | 6 of 98 creators in `data/creators.csv` (53 from India: Gond, Madhubani and Warli artists, regional-language filmmakers, folk musicians) with a "why this fits" line and a look-up link. |

Aesthetics, music and creators are ranked by **cosine similarity** between the Vibe Vector and each
item's numbers (plus shared tags), then **Maximal Marginal Relevance** for variety (`ranking.py`).
A **discovery dial** moves from comfort zone to unfamiliar. **Refine chips** (muted, warmer, dreamier,
less corporate, bolder, more vintage) and **sliders** change the vector and regenerate everything;
**locks** keep any part fixed; **three directions** give Safe, Bold and Weird versions; every change is
kept in a **version history**. Exports: **one-page creative brief (PDF)**, palette **CSS/JSON**, moodboard
**PNG**. The "How this was made" panel shows every number.

**Spark path ("I don't have an idea yet", `spark.py`).** Six tappable questions, one at a time with a
progress trail, each with *Surprise me* and *Skip*: medium, target feeling (up to 2), setting (visual
tiles), era, contrast pair, texture, plus an optional word and "how are you feeling right now". Answers map
into the Vibe Vector through `data/idea_seeds.csv` (30 settings, 20 contrast pairs, 15 textures, 15 story
structures, phrased for each medium; `idea_seeds_labelling_template.csv` lets classmates add more). A
template grammar writes **three ideas (Safe, Bold, Weird)**, each with a title, a logline and a "why this
idea" line quoting the user's answers. **Remix** re-rolls one element; **Lock** keeps one element and
changes the rest; **Use this idea** builds the full universe. Heavy choices only bring a gentle mention
of the Feel tab; ORBIT never diagnoses from the answers.

**Evaluation.** Tests check that crisis wording bypasses Create and Spark, that the universe is complete
and deterministic, that every refine chip changes it, that locks hold, that the three directions differ,
that the discovery dial reaches less-known creators, that **all 64 skip paths** still produce three ideas,
and that Remix changes only the chosen element. In the app, each Spark idea is rated 1-5 for **"Would you
actually make this?"** and **"Does it match your answers?"**, reported per direction in the evaluation.
**Limits.** The word tables, font moods, aesthetics, creators and seeds were labelled by one student, so
they encode one person's taste; colour meaning differs between cultures; the template grammar can sound
formulaic; matching a creator by numbers is a starting point for research, not a judgement of their work.

## The bridges between the two modes

- **Create → Feel.** If an idea, or *"How's the project going?"*, shows stress or creative-block words,
  ORBIT offers a 2-minute breather, a matched game, or a 5-minute exercise for the block (perfectionism,
  fear of judgment, burnout, comparison or no direction). **Back to my project** returns to exactly where
  you were. The words come from a small, readable list (`bridge.py`), checked after the crisis check.
- **Feel → Create.** After a check-in, **Turn this feeling into something** sends the emotion blend into
  Creator Mode, which builds a palette, moodboard and playlist from it (the check-in text is not used as
  the project title).
- **The app changes with you.** A detected feeling (Feel) or the current Vibe Vector (Create) sets the
  whole app's gradient, accent and glow with a smooth fade; sound stays off until you switch it on.
  Create opens with an **orbit view**: your idea at the centre, with palette, type, music, artists and
  aesthetics orbiting as planets, updating as you refine.

## Pattern Insights (My Galaxy → Patterns)

Periods of 7 days, 14 days, 30 days or 1 year, showing how often each feeling family appeared, a mood
line, a calendar heatmap, bright vs low days, and the weekdays and times of day when low moods cluster.
The wording is always "a pattern we noticed", never a diagnosis. If low days are frequent, the
suggestions come in layers: (1) a calming tool or game, (2) the Reach Out Helper, (3) if it lasts
about two weeks, a gentle suggestion to talk to a trusted adult or counsellor, with Tele-MANAS. Every
threshold is a named constant in `patterns.py`, marked as a rule of thumb pending a counsellor's review.
Sparse periods show "Not enough data yet".

## Reach Out Helper (Feel → Reach Out)

**What it does.** For people who find it hard to tell someone how they feel. You choose **who**
(a friend, a parent, a teacher or counsellor) and **how much to share** (just "I'm having a hard
time", a little detail, or more detail with a few words about what it's about). ORBIT shows three
short drafts in **English, Hinglish or Hindi**, matching the language of your last check-in. You edit
one, copy it, and send it **yourself**. ORBIT never sends anything, and a draft is saved only if you
press "Save on this device".

**Method.** Fixed templates (`reach_out.py`), not an AI model, so every possible message is known in
advance and can be checked. The feeling family from the check-in fills in the feeling words.
Language: Devanagari letters → Hindi; Hinglish words found by ORBIT's dictionary → Hinglish; otherwise
English.

**Safety.** After a crisis check-in, or if the "what it's about" box contains crisis wording, the page
shows only the helplines: no drafts, and nothing is kept. After an intense ("concern") message or
repeated low moods, Tele-MANAS and a trusted adult are suggested too. It is offered in Today only after a
sad, scared or angry check-in.

**Evaluation and limits.** Tests check that all 27 combinations (3 people × 3 levels × 3 languages)
give three complete drafts, that language detection works, and that crisis wording produces no drafts
and saves nothing. Thumbs up/down under the drafts are reported in the satisfaction metric. Limits:
templates can sound generic; the Hindi and Hinglish use "raha/rahi" so the user picks their own form;
the drafts were written by the student, not reviewed by a counsellor.

## Mood Studio: palettes and moodboards (Create → Quick palette & music)

**What it does.** Turns your last check-in, or a short vibe such as *"rainy Sunday cafe, nostalgic"*,
into a **5-colour palette** (names, hex codes and a WCAG contrast check), a **font pairing**,
**texture and keyword tiles** and a **moodboard** made only from generated gradients and patterns (no
images, nothing downloaded from the internet). Four sliders (warm-cool, calm-energetic, soft-bold,
vintage-modern) and refine buttons (more muted, warmer, cooler, more contrast, more playful) change the
palette without re-typing the vibe. Export as **PNG, CSS variables or JSON**.

**Method (rule-based, `palette.py`).**
1. Feeling → two numbers on the *circumplex model of affect*: **valence** (pleasant) and **arousal**
   (energy). Each of the 28 emotions has an approximate position, set by the author; a check-in uses the
   score-weighted average. A vibe uses a small keyword table (e.g. *rainy* = calmer, cooler).
2. The feeling's **angle** on that circle picks the **hue** (joy → gold, excitement → coral, anger →
   crimson, sadness → blue, calm → lavender, relief → sage); its distance from neutral and its energy
   set the **saturation**; valence nudges the **lightness**.
3. A **colour-harmony rule** picks the other hues: calm → *analogous* (neighbours), medium →
   *complementary* (opposite), energetic or "more playful" → *triadic* (three evenly spaced).
4. The ink colour is darkened (and, if needed, the primary lightened) until text passes **WCAG AA**:
   4.5 : 1 on the background and 3 : 1 on the primary.
5. Fonts and textures are the closest match to the same numbers. The **How this was made** expander shows
   every number and the rule used.

**Evaluation.** A sweep of 1,620 combinations (valences, arousals, slider positions and refine
settings) gave **0 contrast failures and always 5 valid hex colours**; the tests run a 300-case version of
this on every push. After each palette, a **1-5 "fits the vibe" rating** is stored on the device and the
**average per emotion** is reported in the evaluation.
**Limits.** The emotion-to-colour mapping is the author's rule of thumb, not a scientific law; colour
meaning differs between cultures and people. Fear and anger sit in the same place on the circle, so
they get similar colours. Only about 80 vibe keywords are understood.

## Mood Studio: music discovery (Create → Quick palette & music → Music discovery)

**What it does.** Choose **"Match my mood"** or **"Gently lift me"** (both are always offered for low
moods) and a **discovery dial** from *comfort zone* to *explore*. ORBIT builds a playlist of **10 tracks**
with a one-line "why this" for each, and links that open a **search** on Spotify or YouTube. There are
no API calls and no scraping, and no lyrics are stored. After each playlist: "Did this fit your mood?
(1-5)" and "New to you? (yes/no)", reported in the evaluation as **average fit** and **novelty rate**.

**Data.** `data/music_catalog.csv`: **271 tracks in 24 languages**, hand-labelled by the student with
energy (1-5), valence (1-5), mainstream level (1-5) and tags. It includes Indian indie (Prateek Kuhad, The
Local Train, Anuv Jain, Ritviz), regional music (Tamil, Telugu, Malayalam, Kannada, Bengali, Marathi,
Punjabi, Gujarati, Assamese, Rajasthani folk), Sufi and ghazal, Hindustani and Carnatic classical, and
global music. `data/music_labelling_template.csv` lets classmates add and tag tracks (initials only).

**Method (`music.py`).**
1. **Target vector** from the feeling's valence and arousal (mood and energy on 1-5) plus a few
   preferred tags. "Gently lift me" moves the target one gentle step brighter and steadier (the *iso
   principle*: meet the mood first, then move it), so anger is calmed rather than amplified.
2. **Cosine similarity** between the target and every track's vector [1, mood, energy, tags].
3. The **discovery dial** gives lesser-known tracks a small boost when exploring.
4. **Maximal Marginal Relevance (MMR)** re-ranks for diversity: each next track balances relevance
   against similarity to tracks already chosen (same artist, genre or language). One track per artist.

**Evaluation (measured on the catalogue, discovery 0.5 unless stated):**

| Feeling | Match: mood / energy | Lift: mood / energy | Comfort: mainstream / languages | Explore: mainstream / languages |
|---|---|---|---|---|
| Sadness | 2.0 / 2.0 | 3.5 / 2.1 | 3.6 / 7 | 3.2 / 10 |
| Fear (nervousness) | 2.3 / 3.0 | 3.8 / 2.9 | 3.8 / 5 | 3.1 / 10 |
| Anger | 2.7 / 4.5 | 3.8 / 2.9 | 4.0 / 3 | 3.1 / 10 |
| Joy | 5.0 / 4.6 | 5.0 / 4.8 | 4.5 / 9 | 3.9 / 10 |
| Neutral | 3.2 / 2.2 | 4.3 / 3.2 | 4.4 / 8 | 2.3 / 10 |

"Lift" raises the mood of low-mood playlists by 1.1 to 1.5 points and calms anger's energy (4.5 → 2.9).
Exploring lowers the average mainstream level and puts all 10 tracks in different languages. Tests
check that playlists never repeat an artist, cover at least 3 languages and 5 genres, that lifting is
brighter than matching, and that exploring is less mainstream than the comfort zone.
**Limits.** The catalogue is small and labelled by one person, so energy, valence and "mainstream" are
opinions; the "why this" lines describe those labels, not the actual audio. The numbers above measure
the method against its own labels, not real listeners: only the in-app ratings can show whether
playlists actually fit.

## The AI

**Emotion model:** [`SamLowe/roberta-base-go_emotions-onnx`](https://huggingface.co/SamLowe/roberta-base-go_emotions-onnx), MIT licence.

- **What it is:** RoBERTa, fine-tuned on Google's **GoEmotions** dataset (about 58,000 Reddit
  comments labelled by people). It gives 28 independent emotion scores (multi-label).
- **How it runs:** the quantized ONNX version (about 125 MB) runs on the CPU with `onnxruntime`. It's
  downloaded once into the Hugging Face cache and then works offline.

**ORBIT's own classifier** (`orbit_head.py`) is a softmax regression written in NumPy and
trained on 338 labelled sentences (`data/train_augment.csv`). It reads:
- RoBERTa's scores for the original text,
- RoBERTa's scores for the dictionary-translated text,
- hashed word and character patterns.

It then picks one of 7 emotion families. Its probabilities are softened with **temperature
scaling**, learned from out-of-fold predictions, so the confidence is honest. Retrain it with
`python train_head.py`.

The pipeline (`analysis.py`):
1. **Check:** reject text with no words.
2. **Detect:** RoBERTa scores 28 emotions (Hinglish/Hindi words are translated for readability).
3. **Decide:** the classifier picks the family and its confidence. Below 50%, or for vague
   messages, ORBIT asks instead.
4. **Match:** `match_world()` picks the closest world in that family from `data/worlds.csv`.
5. **Protect:** `safety.py` runs deterministic crisis checks *before* any reply is written.
   Crisis text is never stored, earns no tokens, and gets no games.

**Explainable AI** (`explain.py`) uses *occlusion*: remove one word, re-score, and measure the drop.
The biggest drops are the words that mattered most.

**Companion replies** (`companion.py`) are hand-written templates chosen by the detected emotions.
They reflect the feeling, validate it, remember patterns from the journal, ask one question and
offer one coping tool. If **Ollama** (a free local AI runner) is installed and running, a small local
language model writes the replies instead. Either way, ORBIT says it is an AI, and crisis messages
always get a fixed safety reply.

### Evaluation results (measured)
Methods compared:
- **A:** RoBERTa only
- **B:** RoBERTa + dictionary (v0.3)
- **C:** classifier alone
- **D:** classifier + dictionary (**live**)

| Test | A | B | C | **D** |
|---|---|---|---|---|
| Dev set, macro-F1 (70; optimistic for B and D) | 0.683 | 0.914 | 0.929 | **0.970** |
| Body-feelings set, Fear F1 (33) | – | 0.33 | 0.82 | **0.85** |
| Hinglish/Hindi, out-of-fold macro-F1 (119 training sentences, a fair test) | – | 0.514 | 0.354 | **0.548** |
| Held-out set from classmates | *still to collect (see `docs/data_collection_guide.md`)* | | | |

Each method was adopted only if it met a rule **written before training** (`docs/methodology.md`).

**Safety suite** (93 phrases): crisis recall 98% on the development phrases, with 0 false alarms.
On **fresh** holdouts, crisis recall was 17%, then 33% after improvements. Fixed rules can't foresee
every wording, so helplines are always visible. See `docs/safety_report.md`.

### Creator Mode evaluation

**List diversity (computed on 20 example ideas, `creator_eval.py`):**

| Discovery dial | Languages per playlist (of 8) | Genres per playlist (of 8) | Fields per creator list (of 6) | Average mainstream level (1-5) | Creators from India |
|---|---|---|---|---|---|
| 0 (comfort zone) | 6.2 | 8.0 | 5.6 | 4.25 | 36% |
| 0.5 | 7.8 | 8.0 | 5.8 | 3.74 | 52% |
| 1 (unfamiliar) | 8.0 | 8.0 | 6.0 | 3.05 | 68% |

**Set up but not collected yet** (computed by `evaluation.py` and `creator_eval.py` as soon as data exists):
- **Vibe-prompt accuracy:** about 100 held-out ideas, each rated by 3 people (`docs/vibe_eval_guide.md`).
  ORBIT is compared with a **human baseline** (how often one rater agrees with the other two).
- **In-app ratings:** palette fit, cohesion and music relevance (1-5), music and creator **precision@k**,
  and the **novelty rate**.
- **Timed user study:** creative brief with ORBIT vs usual tools (`docs/user_study.md`).

Claims stay modest: samples will be small and the raters untrained.

**Honest limitations:**
- **Over-reading fear in body sentences.** The classifier now catches body-described anxiety, but it
  reads some harmless body sentences as fear: non-anxiety controls read correctly fell from 77% to 54%.
- **Classifier alone vs dictionary.** On a fair Hinglish test, the classifier on its own was worse
  than the dictionary. That's why the live model D uses both.
- **Who wrote the data.** All current data is author-written. A held-out set from classmates is
  needed for a fair final score.
- **Training data of the base model.** RoBERTa was trained on English Reddit comments. It can
  misread sarcasm and very short messages; for vague messages ORBIT asks first.
- **Small, hand-built datasets.** The training sentences, safety phrases and creative catalogues were
  written for this project (many drafted with an AI assistant), and most labels are one person's view
  (`docs/data_card.md`).
- **Rule-based colour and style mapping.** Feelings become colours, fonts and aesthetics through rules
  of thumb, not science; colour meaning differs between cultures.

## Future scope and scale-up

Each step happens only if the evidence from the step before supports it.

1. **Now (prototype):** both modes, offline-first, with an honest evaluation lab.
2. **Next (school pilot):** consented classmate data (held-out emotions, vibe ratings, user study),
   a fine-tuned Hinglish model, counsellor review of the safety rules and Pattern thresholds, and
   **more Indian languages**.
3. **Later:** user-uploaded **image references** analysed for colour and mood, **team collaboration**
   on shared universes, **licensed music and font APIs** in place of the hand-built catalogues,
   institutional dashboards with only aggregate, anonymous numbers, and regulatory compliance.

**An idea for the future, not built:** opt-in *wellbeing signals*. That could mean screen-time
reflection, on-device detection of distress language shown first to the user, and a trusted contact
notified only if the user authorised it in advance. This would need platform permissions, prominent
disclosure, verifiable parental consent for minors under India's DPDP rules, clinical review and legal
advice. **ORBIT will not monitor private browsing or private messages without the user's knowledge.**

## Safety and privacy
- If someone writes about suicide or self-harm, ORBIT shows **Tele-MANAS 14416 / 1-800-891-4416**
  (Government of India, free, 24/7) and **112** for emergencies, and stops creative suggestions.
- Crisis messages **never reach any AI model**, local or cloud, and are never stored.
- All data (journal, saved worlds, sessions, ratings, corrections) is stored in `data/orbit.db` **on this
  computer only**. It's listed in `.gitignore`, so it's never uploaded. It can be downloaded, imported,
  or deleted.
- Online (Streamlit Community Cloud), each browser session gets its own temporary database, deleted
  within 24 hours; see [docs/deploy.md](docs/deploy.md) for the privacy trade-off.
- Cloud AI replies are optional, need the user's consent, and are protected by a prompt-injection
  guard and an output check.
- ORBIT is a student project, not a medical device, and it doesn't diagnose.

## Project structure

```
Mood-to-World/
├── app.py            # Page settings, landing gate, 3 tabs, Settings menu, background music
├── landing.py        # Landing page: revolving planets, name and age, Start Exploring
├── today.py          # Today: the guided check-in flow
├── onboarding.py     # Accessibility settings
├── settings_ui.py    # Settings menu: display, music, replies, demo mode, export/import
├── wrapped.py        # ORBIT Wrapped: painting, playlist, mood tracker, card
├── views.py          # Mood Lab, saved worlds, Soundspace, collection
├── companion.py      # Companion chat + template replies
├── llm.py            # Optional AI replies (Claude / Ollama) with injection + output guards
├── nudges.py         # "Talk to a real person" nudges
├── feedback_ui.py    # Thumbs up/down and the satisfaction metric
├── constellation.py  # The emotion constellation (SVG) and constellation planets
├── theme.py          # The app takes on the detected feeling's world; background music
├── games.py + games/ # Stress-buster pop-up rules and 9 HTML/JS games
├── reach_out.py      # Reach Out Helper (template drafts the user sends themselves)
├── patterns.py       # Pattern Insights (rule-of-thumb thresholds at the top)
├── letters.py        # Letter you'll never send, letter to future me
├── safety_plan.py    # Safety Plan Builder
├── bridge.py         # Create <-> Feel bridges: block/stress words, exercises
├── creator_eval.py   # Creator Mode evaluation (vibe accuracy, list diversity, user study)
├── studio.py         # Mood Studio screen (palettes and moodboards)
├── create_ui.py      # Create tab: entry, questions, Creative Universe, refine, locks, history, exports
├── spark_ui.py       # Spark path screens
├── vibe.py           # The Vibe Vector, refine chips, sliders, three directions
├── creative.py       # Creative Universe generation (concept, aesthetics, creators, music, moodboard)
├── spark.py          # Spark idea grammar, remix and lock
├── brief.py          # One-page creative brief PDF (Pillow)
├── fonts.py          # Typography pairing from fonts.csv
├── ranking.py        # Cosine similarity and Maximal Marginal Relevance
├── palette.py        # Rule-based palette method, WCAG checks, exports
├── music.py          # Music ranking: cosine similarity + MMR diversity
├── music_ui.py       # Mood Studio music screen
├── styles_features.py # CSS for the newer features
├── demo_mode.py      # Offline demo mode
├── calm_room.py      # Breathing, grounding, thought reframe, gratitude jar
├── journal.py        # Journal charts, insights, emotion galaxy, demo data
├── vending.py        # Arcade vending machine (a state machine)
├── analysis.py       # The shared AI pipeline (classifier, confidence, safety rules, Teach Orbit)
├── orbit_head.py     # ORBIT's trained classifier (NumPy softmax regression, temperature scaling)
├── train_head.py     # Trains classifier variants and applies the pre-registered adoption rules
├── evaluation.py     # Metrics: accuracy, precision, recall, F1, confusion matrix, groups
├── datasets.py       # Loads every labelled dataset + automatic writing-style tags
├── base_scores.py    # Disk cache of RoBERTa scores for labelled sentences
├── teach_ui.py       # "Not quite right?" corrections and clarifying quick answers
├── emotion_model.py  # Loads the model, scores emotions, emotion families
├── hinglish.py       # Hinglish/Hindi to English word translator
├── explain.py        # "Why did ORBIT think this?" (occlusion)
├── safety.py         # Crisis and concern detection, helplines
├── storage.py        # SQLite: local file, or one temporary file per session online; export/import
├── soundscapes.py    # Generated soundscapes and arcade sound effects
├── components.py     # Reusable pieces: planets, cards, saving worlds
├── styles.py         # All the visual design (CSS)
├── world_data.py     # Loads worlds.csv, matches emotions to worlds, Soundspace data
├── requirements.txt / requirements-dev.txt
├── tests/            # 450 pytest tests (safety, translation, analysis, games, Mood Studio, Creator Mode, bridges)
├── .github/workflows/tests.yml   # runs the tests on GitHub on every push
├── docs/
│   ├── methodology.md            # data, modelling, pre-registered rules, results
│   ├── safety_report.md          # safety test rounds and known misses
│   ├── deploy.md                 # Streamlit Cloud: storage, cloud AI, memory
│   ├── data_collection_guide.md  # how to collect the held-out set ethically
│   ├── model_card.md · data_card.md
│   ├── vibe_eval_guide.md · user_study.md   # Creator Mode evaluation protocols
│   └── viva_qa.md · demo_script.md          # viva preparation
├── .streamlit/config.toml + secrets.toml.example
└── data/
    ├── worlds.csv                # aesthetic worlds and their emotion mappings
    ├── train_augment.csv         # 338 training sentences (written for the project)
    ├── eval_set.csv              # 70-sentence development set
    ├── eval_body.csv             # 33-sentence body-feelings test
    ├── eval_heldout_template.csv # template; the real eval_heldout.csv stays local
    ├── safety_tests.csv          # 93 safety phrases with dev/holdout rounds
    ├── music_catalog.csv         # 271 hand-labelled tracks (no lyrics)
    ├── music_labelling_template.csv  # for classmates to add and tag tracks
    ├── fonts.csv                 # 77 Google Fonts tagged by mood
    ├── aesthetics.csv            # 66 art and design movements
    ├── creators.csv              # 98 creators and artists (53 from India)
    ├── idea_seeds.csv            # Spark: settings, contrast pairs, textures, story structures
    ├── idea_seeds_labelling_template.csv
    ├── example_ideas.csv         # 20 ideas for computing list diversity
    ├── vibe_eval_template.csv    # template; the real vibe_eval.csv stays local
    ├── user_study_template.csv   # template; the real user_study.csv stays local
    ├── model/                    # trained classifiers + cached base-model scores
    └── README.md
```

## Tests
```
& "$env:USERPROFILE\.venvs\mood-to-world\Scripts\python.exe" -m pytest -q
```
The tests use a temporary database and never touch real data. GitHub runs them automatically on
every push.

## Setup

You need Python 3.11 or newer (ORBIT is developed on Python 3.12).
pandas 3 and onnxruntime do not support older versions.

The project folder is `Documents\Mood-to-World`. The virtual environment is
kept **outside** the project, at `C:\Users\<you>\.venvs\mood-to-world`.

### Running the app

Open PowerShell in the project folder and run:

```
& "$env:USERPROFILE\.venvs\mood-to-world\Scripts\streamlit.exe" run app.py
```

Your browser opens at `http://localhost:8501`. Press `Ctrl + C` to stop.

### Setting up on a new computer

```
python -m venv "$env:USERPROFILE\.venvs\mood-to-world"
& "$env:USERPROFILE\.venvs\mood-to-world\Scripts\python.exe" -m pip install -r requirements.txt
```

### Optional extras
- **Richer companion replies:** install [Ollama](https://ollama.com), then run `ollama pull llama3.2:3b`.
  ORBIT detects it automatically.
- **Cloud replies with Claude:** `pip install anthropic` (already in requirements.txt), then put your key
  in `.streamlit/secrets.toml` (see `secrets.toml.example`) and opt in under Settings (top right).
