# Data card: ORBIT

Every dataset ORBIT uses, where it came from, how it was labelled, and its limits.
Nothing here contains personal data. Private user data (journal, ratings, letters, safety plan) stays
in `data/orbit.db`, which is git-ignored and never uploaded.

## Emotion data

| File | Rows | What | Source and labelling | Used for |
|---|---|---|---|---|
| `train_augment.csv` | 338 | Sentences with an emotion family, language and writing style | Written for this project; includes body-described feelings and Hinglish/Hindi | Training ORBIT's classifier |
| `eval_set.csv` | 70 | Development sentences | Written for this project; the dictionary was written while looking at them, so scores are **optimistic** | Development only |
| `eval_body.csv` | 33 | Feelings described through the body, plus controls | Written for this project | Measuring the body-feelings fix |
| `eval_heldout_template.csv` | – | Template for 150-200 anonymous classmate sentences | To be collected with teacher permission (`data_collection_guide.md`); the real file stays local and is **never used for tuning** | The final, fair test |
| `safety_tests.csv` | 93 | Crisis, concern and safe phrases in English/Hinglish/Hindi, direct and indirect, with dev/holdout rounds | Written for this project | Measuring crisis recall and false alarms |

## Creative data (Create mode and Mood Studio)

| File | Rows | What | Source and labelling |
|---|---|---|---|
| `worlds.csv` | 8 | Aesthetic "worlds" with palettes, prompts and a motion level | Written for this project |
| `music_catalog.csv` | 271 | Real songs in 24 languages: title, artist, language, genre, energy, valence, mainstream level, tags | Song facts are public; energy/valence/mainstream/tags are **opinions** (one labeller). **No lyrics.** Opened only through search links |
| `music_labelling_template.csv` | – | For classmates to add and tag tracks | Initials only |
| `fonts.csv` | 32 | Google Fonts tagged by mood numbers | Fonts are open-licence Google Fonts (mostly the SIL Open Font License); mood numbers are one labeller's |
| `aesthetics.csv` | 66 | Art and design movements, including Indian traditions (Madhubani, Warli, Gond, Pattachitra, truck art) | Public art-history facts; numbers and cues are one labeller's |
| `creators.csv` | 98 | Creators and artists (53 from India) with a short factual "known for" line | Public facts, kept short and checkable; numbers are one labeller's. No images are stored |
| `idea_seeds.csv` | 80 | 30 settings, 20 contrast pairs, 15 textures, 15 story structures | Written for this project |
| `idea_seeds_labelling_template.csv` | – | For classmates to add seeds | Initials only |
| `example_ideas.csv` | 20 | Example ideas for computing list diversity | Written for this project |
| `vibe_eval_template.csv` | – | About 100 anonymous ideas x 3 raters (mood, energy, warmth, era 1-5) | To be collected; the real `vibe_eval.csv` stays local |
| `user_study_template.csv` | – | Timed brief-building study | To be collected; the real `user_study.csv` stays local |

## How the data was made

Many of these files (the training and evaluation sentences, safety phrases, and the creative catalogues)
were **drafted with help from an AI coding assistant** and then used by the student. Facts about real
songs, fonts, art movements and creators should be **checked by the student** before relying on them,
and every label is an opinion until classmates' ratings are collected.

## Known gaps and biases

- **One labeller.** Almost every number was set by one person (with AI help); inter-rater agreement is not yet
  measured (the vibe-evaluation template is designed to measure it).
- **Language balance.** English and Hindi dominate the music catalogue; regional languages have only
  a few tracks each.
- **Mainstream bias.** Well-known artists are easier to recall, so the catalogue leans mainstream; the
  discovery dial and MMR partly correct for this.
- **Body and sarcasm.** The emotion data has few sarcastic or very short messages.

## Consent and privacy rules for collecting more data

- Teacher permission, voluntary participation, and the right to withdraw.
- No names, phone numbers, or details that identify anyone; initials only for labellers.
- Classmates' sentences and ratings stay on the project computer and are git-ignored.
- Crisis-type sentences are not collected from classmates; safety phrases are written for the project.
