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

## 6. Confidence
The classifier's top probability is its confidence. When it is low, ORBIT asks
a gentle clarifying question instead of asserting a feeling. Thresholds are set
on cross-validation results from the training data.

## 7. Human in the loop ("Teach Orbit")
Users can correct ORBIT. Corrections are stored locally (never uploaded) and
can be added to training. The AI Lab reports metrics before and after.
Correction texts are never part of any test set.
