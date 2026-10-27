# Viva questions and answers

Short, honest answers. Numbers come from `docs/methodology.md`.

**1. How is ORBIT different from ChatGPT?**
ChatGPT is a general chatbot: it writes whatever fits the prompt, and you can't see why. ORBIT is
built for two specific jobs and shows its working. Feelings are read by a pre-trained emotion model
plus my own trained classifier, with confidence and a "why" heatmap. Creative outputs come from one
**Vibe Vector** through rules anyone can inspect (colour-wheel harmony, WCAG contrast, cosine
similarity, Maximal Marginal Relevance). Crisis handling never uses an AI model. It also runs offline,
understands Hinglish, and keeps data on the device. An AI model is optional and only polishes text,
always with a template fallback.

**2. How do you make sure the outputs are cohesive?**
Every output is generated from the same Vibe Vector (valence, arousal, brightness, warmth, era,
texture, boldness, themes). The palette, fonts, moodboard, aesthetics, music and creators all read
those same numbers, so a "warm, nostalgic, calm" idea gets warm colours, a vintage serif, film grain,
nostalgic songs and creators near that point. Refining changes the vector, and everything updates
together. Cohesion is also rated by users (1-5) under each universe.

**3. What if it misses a crisis?**
It can, and I measured that honestly. Crisis recall was 98% on development phrases but only 17% and then
33% on fresh holdout rounds, because fixed rules can't foresee every wording. So the crisis check is
one layer, not the only one: helplines (Tele-MANAS 14416, 112) are always reachable and on the
landing page, concern-level messages get a gentle note, repeated low moods trigger
a "talk to someone" suggestion, and there is a Safety Plan. ORBIT says clearly that it is not a crisis
service.

**4. Where does the data come from?**
The emotion base model was trained by its authors on about 58,000 Reddit comments (GoEmotions). My
classifier was trained on 338 sentences written for this project, many drafted with an AI assistant.
The creative catalogues (271 songs, 32 fonts, 66 aesthetics, 98 creators, 80 idea seeds) were also
written for this project; song and creator facts are public, and the numbers are one labeller's
opinions. There are no lyrics or scraped images. Templates are ready to collect anonymous classmate
data with teacher permission. See `data_card.md`.

**5. How did you evaluate it?**
- Emotions: four methods (A-D) compared on a development set, a body-feelings set and a fair
  out-of-fold Hinglish test, with rules for adopting a method written *before* training. The live
  model D reached Hinglish macro-F1 0.548 against 0.514 for the dictionary alone.
- Safety: a 93-phrase suite with dev and holdout rounds.
- Creator Mode: computed list diversity (with the discovery dial at "unfamiliar", every playlist
  covers 8 languages and the average mainstream level drops from 4.25 to 3.05), plus prepared
  people-based tests: vibe accuracy against a human baseline, ratings, precision@k, novelty, and a
  timed user study.
- 450 automated tests run on every push.
- Limits: small samples and one labeller.

**6. Why two modes?**
Creative work and feelings are tangled: being stuck, comparison and burnout are emotional. Create
turns ideas into direction; Feel supports wellbeing. The bridges connect them. "I'm stuck" in Create
offers a short break, game or block exercise and then returns you to your project. "Turn this
feeling into something" in Feel sends your emotion blend into Create.

**7. Why not train your own model from scratch?**
Training a language model needs far more data and computing power than a school project has. A
pre-trained model gives strong English emotion scores. My contribution is the classifier on top for
Hinglish, body feelings and calibrated confidence, plus the evaluation, safety layer and Creator Mode.

**8. What are the privacy risks?**
Journals are sensitive. So everything stays on the device (or in a temporary session online), can be
downloaded from Settings, and nothing is uploaded unless the user opts in to cloud
replies. Crisis text is never stored. There is no monitoring of other apps or messages.

**9. How is it different from Wysa?**
Wysa is a professional mental-health app built with clinical input, which also offers access to human
support (check its current features before the viva). ORBIT is a student project and doesn't claim clinical value. Its focus is different:
helping young **creators**, explainable and offline-first AI, Hinglish support, and turning feelings into
creative direction.
