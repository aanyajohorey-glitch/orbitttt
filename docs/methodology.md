# ORBIT methodology (data science and evaluation)

This document follows the CBSE AI Project Cycle and records decisions **before**
results were known, so the evaluation stays honest.

## 1. Problem scoping
Teenagers often find it hard to name and handle feelings, especially around
exams. ORBIT helps them **name** a feeling (emotion detection), **feel heard**
(companion), **cope** (Calm Room) and **notice patterns** (Journal). It is not a
therapist and does not diagnose.

## 2. Data
| File | Role | Who wrote it | Used for training? |
|---|---|---|---|
| `data/train_augment.csv` (338 sentences) | Training data for ORBIT's classifier, including body-described anxiety and non-anxiety body controls | Author-written | **Yes** |
| `data/eval_set.csv` (70) | Original development set | Author-written | No, but the Hinglish dictionary was built while looking at it, so its Hinglish scores are **optimistic** |
| `data/eval_body.csv` (33) | Focused test: feelings described through the body (20 anxiety, 13 controls) | Author-written | No |
| `data/eval_heldout.csv` (target 150 to 200; local only, git-ignored; template in `eval_heldout_template.csv`) | **Fair test**: classmates' anonymous sentences | Classmates (with teacher permission) | **Never**; not used for tuning either |
| Teach Orbit corrections | Labels users give when ORBIT was wrong | Users, stored only on their own computer | Optional, when the user retrains |
| `data/safety_tests.csv` (93) | Safety-rule test suite | Author-written | Used to write rules (dev rounds); see `docs/safety_report.md` |

**Leakage check:** no training sentence is identical to a test sentence, and
none shares 50% or more of its words with one (checked automatically). Eight
near-duplicates were found and rewritten before training.

## 3. Modelling
1. **Base model:** pre-trained RoBERTa (GoEmotions, ONNX). It gives 28 emotion
   scores, which are grouped into 7 families.
2. **ORBIT classifier:** a small softmax (multinomial logistic) regression,
   written in NumPy so every step can be explained. Its inputs are:
   - the base model's 28 scores (the "model outputs" layer),
   - the 7 family totals,
   - hashed word and character n-grams of the **original** text. These let it
     learn Hinglish/Hindi spellings and body-sensation phrases **without** the
     hand-written dictionary.

   Regularisation strength is chosen by **5-fold cross-validation on the
   training data only**.

## 4. Evaluation
For each test set, ORBIT reports:
- accuracy and **macro-F1**, plus **per-family precision, recall and F1**;
- a **confusion matrix**;
- results split by **language** and **writing style** (Body-based, Very short,
  Informal / slang, Standard; tagged automatically by `datasets.writing_style`).

## 5. Pre-registered adoption rule (written before training)
The ORBIT classifier replaces "base model + dictionary" as the deciding layer
**only if both** of these hold:
1. **Fear F1 on `eval_body.csv` improves** by at least 0.10, and
2. **macro-F1 on `eval_set.csv` drops by no more than 0.03.**

If the held-out set exists, its results are reported but **not** used to tune
anything. A large gap between the dev and held-out results is itself a
finding to report.

### 5a. Result of rule 1, and two problems found afterwards
Rule 1 was met (body Fear F1 0.33 → 0.82; dev macro-F1 0.914 → 0.929), so
classifier **C** was adopted. The fuller evaluation in the AI Lab then showed
two problems:
1. **Over-predicting fear on body sentences that are not anxiety.** Controls
   read correctly fell from 77% to 54% (for example "my hands are cold, I forgot
   my gloves" became Fear). Rule 1 did not include the controls. That was an
   oversight in the rule, and it is reported here rather than changed afterwards.
   Fixing it properly needs new training controls **and** a new test set,
   because the current body set has now been looked at.
2. **Hinglish got worse on a fair test.** On the 119 Hinglish/Hindi
   *training* sentences, which the dictionary never saw, scored out-of-fold,
   classifier C reached macro-F1 0.35 against 0.51 for the dictionary (B).
   About 95 Hinglish training sentences per fold are not enough for C to learn
   Hinglish alone.

### 5b. Pre-registered rule 2 (written before training variant D)
Variant **D** ("translation-assist") is C plus the base model's scores on the
dictionary-translated text as extra features. D replaces C **only if all** of
these hold:
1. out-of-fold macro-F1 on the Hinglish/Hindi training sentences improves by
   at least 0.05 over C;
2. body-set Fear F1 drops by no more than 0.03 compared with C;
3. dev macro-F1 drops by no more than 0.03 compared with C.

### 5c. Result of rule 2
| Measure | C | D |
|---|---|---|
| Out-of-fold Hinglish/Hindi macro-F1 (119 training sentences; dictionary baseline B = 0.514) | 0.354 | **0.548** |
| Body-set Fear F1 (B = 0.33) | 0.82 | **0.85** |
| Dev macro-F1 (B = 0.914) | 0.929 | **0.970** (optimistic: the dictionary was built on dev) |
| Body non-anxiety controls read correctly (B = 77%) | 54% | 54% |

All three conditions were met, so **D is the live model**. The control
problem from 5a remains open.

## 6. Confidence
The classifier's top probability is its confidence. When it is below **50%**,
ORBIT asks a gentle clarifying question instead of asserting a feeling. The
threshold was chosen from out-of-fold predictions on the training data. For
the live model D:
- below 50% confidence, only 30% of answers are right;
- at 80% or more, 92% are right;
- at the threshold, ORBIT is confident on 87% of messages, with 84% accuracy.

**Two later findings, and the fixes:**
1. **Temperature scaling.** The weakly regularised model gave over-confident
   probabilities. One temperature T is fitted to the out-of-fold logits by
   minimising log-loss (D: T = 1.64; log-loss 0.807 → 0.715). It does not change
   which family wins, so accuracy and F1 are unchanged. It only makes
   confidence more honest: at the 50% threshold, ORBIT is confident on 78% of
   messages with 89% accuracy.
2. **Vague-message guard.** On short or vague messages unlike the training data,
   the model stayed confident even after scaling ("today was weird" → anger
   98%). Messages of 3 words or fewer, or with vague phrases ("idk",
   "weird", "okay", "kuch nahi"…), always get a clarifying question. This is
   a documented rule, not a learned one.

## 7. Human in the loop ("Teach Orbit")
Users can correct ORBIT. Corrections are stored locally (never uploaded) and
can be added to training. The AI Lab reports metrics before and after.
Correction texts are never part of any test set.
