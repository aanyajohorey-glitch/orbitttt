# Collecting the held-out test set (`data/eval_heldout.csv`)

The held-out set is ORBIT's **fair exam**. It holds 150 to 200 sentences that
classmates write and that the developer has **never** used to build or tune
anything: not the Hinglish dictionary, not the classifier, not the safety rules.

## Before you start
1. **Get your teacher's permission** and explain the purpose to the class.
2. Participation is **voluntary**. Anyone can stop or withdraw their sentences.
3. Collect sentences **anonymously** (for example a paper slip or an anonymous
   form). Do **not** record names, roll numbers, emails or anything that
   identifies a person or anyone else.
4. Ask for **everyday feelings only**. Do **not** collect sentences about
   self-harm or suicide; safety phrases are tested separately and
   responsibly (see `docs/safety_report.md`). If a slip suggests a student is
   in distress, give it to the teacher straight away.

## What to ask
> "Write one or two sentences about how you felt at some point this week, the
> way you would text a friend. English, Hinglish or Hindi are all fine. Please
> don't include names."

Aim for a balance:
- about **25 sentences per emotion family** (7 families × 25 ≈ 175);
- a mix of **English, Hinglish and Hindi**, with at least 40 that are not English;
- different styles: short messages, long ones, slang, and feelings described
  through the body ("my hands were shaking").

## Labelling
Each sentence gets **one** `emotion_family`, the main feeling:

| Family | Includes | Example |
|---|---|---|
| Joy | happiness, excitement, pride, relief, optimism, amusement | "Finally got my results, so happy!" |
| Warmth | love, care, gratitude, admiration, longing | "Thank you mom for staying up with me." |
| Sadness | sadness, grief, disappointment, regret | "Nobody sat with me at lunch today." |
| Fear | fear, nervousness, anxiety, embarrassment | "My hands won't stop shaking before the exam." |
| Anger | anger, annoyance, disgust, disapproval | "So unfair, I got blamed for nothing." |
| Wonder | curiosity, confusion, surprise, realisation | "Wait, how does that even work?" |
| Neutral | facts, no clear feeling | "I have tuition at 5." |

**Best practice:** have **two people label independently**, then compare. Count
how often they agree (the agreement rate); this is worth reporting. Discuss
disagreements and agree a final label, or remove sentences that are too unclear.

`language` must be `English`, `Hinglish` or `Hindi`.

## File format
```
text,language,emotion_family
"Finally got my results, so happy!",English,Joy
aaj bahut bore ho raha hai,Hinglish,Neutral
```
Put text that contains commas inside "double quotes". Save as UTF-8, especially
for Hindi.

## The golden rule
**Never look at ORBIT's mistakes on this file and then change ORBIT to fix
them.** If you do, the score stops being fair. If you want to improve ORBIT
after testing, collect a **new** held-out set for the next round.
