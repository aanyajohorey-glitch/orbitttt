# ORBIT

*Every feeling has a universe.*

A Class 12 CBSE Artificial Intelligence project. You describe how you
feel, and ORBIT turns it into a personalised aesthetic world: a palette,
textures, a creative prompt and a music vibe.

Built with **Python**, **Streamlit** and **pandas**.

> Status: prototype v0.2. The emotion model powers both **Home** and the
> **Mood Lab**.

## The AI model

ORBIT uses a **pre-trained** emotion model:
[`SamLowe/roberta-base-go_emotions-onnx`](https://huggingface.co/SamLowe/roberta-base-go_emotions-onnx)
(MIT licence).

- **What it is:** RoBERTa, a transformer language model, fine-tuned on
  Google's **GoEmotions** dataset (about 58,000 Reddit comments labelled
  by people with 27 emotions plus "neutral").
- **What it does:** gives every one of the 28 emotions its own score from
  0 to 1 (multi-label), so mixed feelings like "excited but nervous" show
  up as two emotions.
- **How ORBIT runs it:** the small quantized ONNX version (about 125 MB),
  using `onnxruntime` on the computer's CPU. It's downloaded once into
  the Hugging Face cache (`C:\Users\<you>\.cache\huggingface`) and then
  works offline. No API key and no cost.
- **How a world is chosen:** each world in `data/worlds.csv` lists the
  emotions it belongs to. ORBIT adds up the model's scores for those
  emotions and recommends the world with the highest total
  (`match_world()` in `world_data.py`).
- **Limitations:** English only; it can misread sarcasm and very short
  texts; it has no labels for nostalgia, loneliness or calm, so those
  worlds are matched through nearby emotions (love, grief, neutral).

## Pages

| Page | What it does |
|---|---|
| Home | Describe your feelings, pick an optional creative intent and press **Find my orbit**. The emotion model detects your emotions and ORBIT recommends a matching world with a prompt for your intent. Also shows example worlds. |
| Mood Lab | Runs the emotion model on your description: primary emotion, intensity, top five emotions and a suggested world you can save. |
| Vending Machine | Choose a mystery capsule to reveal a random creative pack. You can reroll or save it. |
| ORBIT | Your universe: every saved world as a planet. Open one to see its details. |
| Soundspace | Music-vibe suggestions (genres, tempo, moods). It doesn't play music. |
| My Collection | A list of saved worlds. Saved worlds reset when the session ends. |

## Project structure

```
Mood-to-World/
├── app.py               # Main file: page settings, navigation, picks the page to show.
├── views.py             # One function per page (Home, Mood Lab, ...).
├── components.py        # Reusable pieces: planets, cards, saving worlds, details pop-up.
├── world_data.py        # Sample content; loads data/worlds.csv with pandas; matches emotions to worlds.
├── emotion_model.py     # Loads the pre-trained emotion model and scores 28 emotions.
├── styles.py            # Colours, fonts, glass cards and planets (CSS).
├── requirements.txt     # Python packages the app needs.
├── README.md            # This file.
├── .streamlit/
│   └── config.toml      # Streamlit theme colours.
└── data/
    ├── worlds.csv       # The sample aesthetic worlds.
    └── README.md        # Explains the data files.
```

## Setup

You need Python 3.11 or newer (ORBIT is developed on Python 3.12).
pandas 3 and onnxruntime do not support older versions.

The project folder is `Documents\Mood-to-World`. The virtual environment
(the separate place where Streamlit is installed) is kept **outside** the
project, at `C:\Users\aakal\.venvs\mood-to-world`. This keeps it out of
OneDrive and avoids Windows' long-path problems.

### Running the app (already set up on this computer)

1. Open PowerShell in the project folder.

2. Turn on the virtual environment:

   ```
   & "$env:USERPROFILE\.venvs\mood-to-world\Scripts\Activate.ps1"
   ```

   If PowerShell blocks this with an "execution policy" error, skip this
   step and use the full path in step 3 instead:
   `& "$env:USERPROFILE\.venvs\mood-to-world\Scripts\streamlit.exe" run app.py`

3. Run the app:

   ```
   streamlit run app.py
   ```

   Your browser will open at `http://localhost:8501`.

To stop the app, press `Ctrl + C` in the terminal.

### Setting up on a new computer

1. Create the virtual environment:

   ```
   python -m venv "$env:USERPROFILE\.venvs\mood-to-world"
   ```

2. Turn it on (see step 2 above), then install the required packages:

   ```
   pip install -r requirements.txt
   ```
