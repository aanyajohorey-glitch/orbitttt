# Model card: ORBIT

ORBIT combines one pre-trained neural model with small, explainable components built for this
project. This card follows the usual model-card headings (details, intended use, data, evaluation,
limitations, ethics).

## 1. Model details

| Component | What it is | Where |
|---|---|---|
| Base emotion model | `SamLowe/roberta-base-go_emotions-onnx`: RoBERTa fine-tuned on GoEmotions (about 58,000 English Reddit comments), 28 emotion scores, quantized ONNX (~125 MB), MIT licence | `emotion_model.py` |
| ORBIT classifier (variant **D**, live) | Softmax regression in NumPy on: RoBERTa scores for the original text, RoBERTa scores for the dictionary-translated text, hashed word and character n-grams. 7 emotion families; temperature scaling (T = 1.64) | `orbit_head.py`, `train_head.py` |
| Offline estimate (variant **T**) | The same classifier type on text features only, for demo mode when the base model can't load (out-of-fold accuracy 0.45) | `demo_mode.py` |
| Hinglish/Hindi dictionary | Hand-written word and phrase translations | `hinglish.py` |
| Safety rules | Deterministic phrases and patterns for crisis and concern; never an AI model | `safety.py` |
| Explanation | Occlusion: remove one word, re-score, measure the drop | `explain.py` |
| Vibe Vector and Creative Universe | Rule-based: word tables -> valence, arousal, brightness, warmth, era, texture, boldness; palette by colour-wheel rules; fonts, aesthetics, music and creators ranked by cosine similarity + Maximal Marginal Relevance | `vibe.py`, `palette.py`, `fonts.py`, `creative.py`, `music.py`, `ranking.py` |
| Optional language model | Claude (cloud, needs a key and user consent) or Ollama (local) for warmer replies and an optional concept polish. Always guarded (prompt-injection check, output check) with a template fallback; never used for crisis messages | `llm.py` |

## 2. Intended use

- Helping teenagers and young creators **name a feeling**, try a small coping tool, and reach real
  people (Feel mode).
- Turning an idea or feeling into a **cohesive creative direction** (Create mode).
- A school AI project that shows its method, evaluation and limits openly.

**Not intended for:** diagnosis, therapy, crisis counselling, monitoring anyone, or any decision about
a person. ORBIT is not a medical device.

## 3. Training and evaluation data

See [`data_card.md`](data_card.md). In short: the classifier was trained on 338 sentences written for
the project; evaluation sets were also written for the project (70 development, 33 body-feelings), and a classmate
held-out set (150-200 anonymous sentences, with teacher permission) is still to be collected.

## 4. Evaluation (measured; details in the AI Lab and `methodology.md`)

| Test | A: RoBERTa only | B: + dictionary | C: classifier | **D: live** |
|---|---|---|---|---|
| Development set macro-F1 (70; optimistic for B and D) | 0.683 | 0.914 | 0.929 | **0.970** |
| Body-feelings set, Fear F1 (33) | – | 0.33 | 0.82 | **0.85** |
| Hinglish/Hindi out-of-fold macro-F1 (119, a fair test) | – | 0.514 | 0.354 | **0.548** |

- **Safety suite** (93 phrases, English/Hinglish/Hindi, direct and indirect): crisis recall 98% on
  development phrases with 0 false alarms, but only 17% and then 33% on fresh holdout rounds. This is
  why helplines are always visible and crisis rules are only one layer.
- **Creator Mode:** computed list diversity (AI Lab). People-rated vibe accuracy, in-app ratings and
  the timed user study are set up but **not collected yet**.

## 5. Limitations

- **Small, hand-built data.** Most labels were set by one labeller (with AI help), so they encode one view.
- **English-trained base model.** RoBERTa learned from English Reddit; Hinglish and Hindi go through a
  dictionary and a small classifier, and sarcasm or very short messages are often misread.
- **Body-feelings trade-off.** Catching "my heart is racing" as fear made some harmless body
  sentences read as fear (controls fell from 77% to 54%).
- **Rule-based creativity.** The emotion-to-colour mapping, font moods, aesthetic and creator
  positions are rules of thumb, not science; colour meaning differs between cultures.
- **Safety rules miss new wordings.** Fresh holdout recall was low; ORBIT must never be the only
  safety net.

## 6. Ethical considerations

- Crisis handling is deterministic, runs first in both modes, never uses an AI model, and the crisis
  text is never stored.
- No covert monitoring: ORBIT only reads what the user types or says into ORBIT.
- Data stays on the device (or one temporary session online), can be exported, and is deleted by
  Panic wipe. Nothing is uploaded unless the user turns on cloud replies (with clear consent).
- Teenagers are the users: onboarding explains that ORBIT is an AI, not a therapist, and suggests
  telling a trusted adult.
