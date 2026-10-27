"""
soundscapes.py
ORBIT makes its own calming sounds with maths. No music files, no streaming.

Every sound is a list of numbers (samples) made from:
- sine waves        -> pure musical notes and soft chords
- random noise      -> rain, wind and waves (filtered to sound softer)
- envelopes         -> slow fades so the sound swells and breathes

The samples are saved as a WAV file in memory and played with st.audio.
Short "arcade" effects (coin, button beep, motor, chime) for the Vending
Machine are made the same way.
"""
import io
import wave

import numpy as np
import streamlit as st

RATE = 16000


def to_wav(samples):
    """Turn numbers between -1 and 1 into WAV file bytes."""
    samples = np.clip(samples, -1, 1)
    pcm = (samples * 32767 * 0.9).astype(np.int16)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(RATE)
        file.writeframes(pcm.tobytes())
    return buffer.getvalue()


def smooth(signal, width):
    """A simple low-pass filter (moving average): makes noise softer."""
    kernel = np.ones(width) / width
    return np.convolve(signal, kernel, mode="same")


def seamless(samples, fade_seconds=1.5):
    """Blend the end into the start so the loop has no click."""
    fade = int(fade_seconds * RATE)
    ramp = np.linspace(0, 1, fade)
    body = samples[:-fade].copy()
    body[:fade] = body[:fade] * ramp + samples[-fade:] * (1 - ramp)
    return body


def normalise(samples, level=0.6):
    return samples / (np.max(np.abs(samples)) + 1e-9) * level


def chord(freqs, seconds, wobble=0.12):
    t = np.arange(int(seconds * RATE)) / RATE
    out = np.zeros_like(t)
    for i, f in enumerate(freqs):
        swell = 0.6 + 0.4 * np.sin(2 * np.pi * (wobble + i * 0.03) * t + i)
        out += swell * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t))
    return out


@st.cache_data(show_spinner=False)
def soundscape(kind, seconds=24):
    rng = np.random.default_rng(7)
    n = int(seconds * RATE)
    t = np.arange(n) / RATE
    if kind == "rain":
        hiss = smooth(rng.normal(0, 1, n), 6)
        drops = np.zeros(n)
        for start in rng.integers(0, n - 400, 260):
            drops[start:start + 400] += rng.uniform(0.3, 1) * np.exp(-np.arange(400) / 50) * np.sin(
                2 * np.pi * rng.uniform(1800, 3200) * np.arange(400) / RATE)
        sound = 0.55 * hiss + 0.25 * drops
    elif kind == "waves":
        surf = smooth(rng.normal(0, 1, n), 30)
        swell = (0.5 + 0.5 * np.sin(2 * np.pi * t / 8)) ** 2
        sound = surf * (0.15 + swell)
    elif kind == "dream":
        sound = chord([220.0, 261.6, 329.6, 392.0, 493.9], seconds)
    elif kind == "sunset":
        sound = chord([196.0, 246.9, 293.7, 370.0], seconds, wobble=0.08)
    elif kind == "focus":
        drone = chord([110.0, 164.8], seconds, wobble=0.05)
        air = smooth(rng.normal(0, 1, n), 60) * 0.6
        sound = drone + air
    elif kind == "night":
        crickets = np.zeros(n)
        for start in range(0, n - 3000, int(0.9 * RATE)):
            burst = np.arange(3000) / RATE
            chirp = np.sin(2 * np.pi * 4200 * burst) * (np.sin(2 * np.pi * 30 * burst) > 0)
            crickets[start:start + 3000] += chirp * np.hanning(3000) * rng.uniform(0.2, 0.5)
        sound = 0.25 * crickets + chord([146.8, 220.0], seconds, wobble=0.04) * 0.5
    else:
        raise ValueError(kind)
    return to_wav(seamless(normalise(sound)))


def _tone(freq, seconds, decay=8.0):
    t = np.arange(int(seconds * RATE)) / RATE
    return np.sin(2 * np.pi * freq * t) * np.exp(-decay * t)


@st.cache_data(show_spinner=False)
def sfx(kind, variant=0):
    """A short arcade sound. `variant` adds a few silent samples so that the
    same sound twice in a row is a 'new' file and the browser plays it again."""
    if kind == "coin":
        sound = np.concatenate([_tone(1318, 0.09, 20), _tone(1760, 0.35, 9)])
    elif kind == "beep":
        sound = _tone(880, 0.08, 25)
    elif kind == "error":
        sound = np.concatenate([_tone(330, 0.12, 10), _tone(262, 0.2, 10)])
    elif kind == "vend":
        t = np.arange(int(1.4 * RATE)) / RATE
        motor = np.sign(np.sin(2 * np.pi * 70 * t)) * 0.25 * (0.6 + 0.4 * np.sin(2 * np.pi * 6 * t))
        thunk = np.zeros(int(0.5 * RATE))
        thunk[:4000] = np.sin(2 * np.pi * 90 * np.arange(4000) / RATE) * np.exp(-np.arange(4000) / 700)
        sound = np.concatenate([smooth(motor, 8), thunk])
    elif kind == "chime":
        length = int(1.6 * RATE)
        sound = np.zeros(length)
        for i, f in enumerate([784, 988, 1175, 1568]):
            note = _tone(f, 0.9, 4)
            start = i * 1600
            sound[start:start + len(note)] += note[: length - start]
    else:
        raise ValueError(kind)
    return to_wav(np.concatenate([normalise(sound, 0.5), np.zeros(8 * variant)]))
