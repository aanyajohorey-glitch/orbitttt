"""
emotion_model.py
ORBIT's emotion detector.

We use a PRE-TRAINED model: SamLowe/roberta-base-go_emotions-onnx
- It is a RoBERTa language model fine-tuned on Google's GoEmotions dataset
  (about 58,000 Reddit comments, each labelled with emotions by people).
- It gives a score from 0 to 1 for each of 28 emotions. The scores are
  independent, so a text can be both "excitement" 0.7 and "nervousness" 0.2.
- We use the small "quantized" ONNX version (about 125 MB). It runs on the
  laptop's CPU with onnxruntime, with no internet needed after the first
  download and no paid API.

How it works, step by step:
1. The tokenizer splits the text into tokens (pieces of words) and turns
   them into numbers.
2. The model reads those numbers and outputs 28 raw scores ("logits").
3. The sigmoid function turns each raw score into a value between 0 and 1.
"""
import json

import numpy as np
import onnxruntime
import streamlit as st
from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer

MODEL_REPO = "SamLowe/roberta-base-go_emotions-onnx"
MODEL_FILE = "onnx/model_quantized.onnx"
TOKENIZER_FILE = "onnx/tokenizer.json"
CONFIG_FILE = "onnx/config.json"


def get_file(filename):
    """Use the downloaded copy if we have one; otherwise download it once.

    Files are kept in the Hugging Face cache folder on this computer
    (C:\\Users\\<you>\\.cache\\huggingface), not in the project folder.
    """
    try:
        return hf_hub_download(MODEL_REPO, filename, local_files_only=True)
    except Exception:
        return hf_hub_download(MODEL_REPO, filename)


@st.cache_resource(show_spinner="Loading the emotion model…")
def load_model():
    """Load the model, tokenizer and emotion names.

    @st.cache_resource means this happens only once while the app runs,
    not on every button click.
    """
    session = onnxruntime.InferenceSession(
        get_file(MODEL_FILE), providers=["CPUExecutionProvider"]
    )

    tokenizer = Tokenizer.from_file(get_file(TOKENIZER_FILE))
    tokenizer.enable_truncation(max_length=512)  # the model's maximum length

    with open(get_file(CONFIG_FILE), encoding="utf-8") as file:
        id_to_label = json.load(file)["id2label"]
    labels = [id_to_label[str(number)] for number in range(len(id_to_label))]

    return {"session": session, "tokenizer": tokenizer, "labels": labels}


def detect_emotions(text):
    """Return all 28 emotions with their scores, highest first.

    Example: [("excitement", 0.68), ("nervousness", 0.16), ...]
    """
    model = load_model()

    # 1. Text -> token numbers
    encoding = model["tokenizer"].encode(text)
    inputs = {
        "input_ids": np.array([encoding.ids], dtype=np.int64),
        "attention_mask": np.array([encoding.attention_mask], dtype=np.int64),
    }

    # 2. Token numbers -> 28 raw scores
    logits = model["session"].run(None, inputs)[0][0]

    # 3. Raw scores -> values between 0 and 1 (sigmoid)
    scores = 1 / (1 + np.exp(-logits))

    results = [(label, float(score)) for label, score in zip(model["labels"], scores)]
    results.sort(key=lambda pair: pair[1], reverse=True)
    return results


def describe_intensity(score, emotion=None):
    """Turn the top emotion's score into a simple word.

    A high "neutral" score means the model is sure there is NO strong
    emotion, so it is described as "Low" rather than "Strong".
    """
    if emotion == "neutral":
        return "Low"
    if score >= 0.6:
        return "Strong"
    if score >= 0.3:
        return "Moderate"
    return "Gentle"
