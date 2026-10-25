# Collecting the vibe-prompt evaluation set

Goal: about **100 creative ideas** that ORBIT has never seen, each rated by **3 people**, to measure
how well the Vibe Vector matches what people feel an idea is like.

## Before you start
- Get your teacher's permission. Participation is voluntary and anyone can withdraw.
- Ideas must be anonymous: no names, no phone numbers, nothing that identifies anyone.
- Don't use these ideas to tune ORBIT. They are only for testing (otherwise the score is optimistic).
- The real file, `data/vibe_eval.csv`, stays on the project computer (it is git-ignored).

## Step 1: collect ideas
Ask classmates for one short idea each, in English, Hinglish or Hindi, e.g. *"a poster about
Diwali night in my building"*. Aim for a mix of moods, mediums and languages.

## Step 2: rate every idea three times
Three raters (initials only: A, B, C) rate each idea **without seeing ORBIT's output**, on 1-5:

| Scale | 1 | 3 | 5 |
|---|---|---|---|
| mood | very dark / sad | in-between | very bright / happy |
| energy | very calm | steady | very energetic |
| warmth | very cool (blues) | neutral | very warm (oranges) |
| era | ancient / mythic | today | futuristic |

## Step 3: fill in the template
Copy `data/vibe_eval_template.csv` to `data/vibe_eval.csv`. One row per idea per rater:
`idea_id, idea, language, rater, mood, energy, warmth, era`.

## Step 4: read the results in the AI Lab
About & AI Lab -> Creator Mode -> *Vibe-prompt accuracy*. For each scale it shows:
- **ORBIT:** how often ORBIT is within 1 point of the raters' median;
- **Human baseline:** how often one rater is within 1 point of the other two raters' median.

If ORBIT is close to the human baseline, it agrees with people about as well as people agree with
each other. Report the number of ideas and remember the sample is small.
