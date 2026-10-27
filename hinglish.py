"""
hinglish.py
Basic Hinglish and Hindi support for ORBIT.

The emotion model was trained on English, so Hinglish ("aaj mood bahut
kharab hai") or Hindi ("मैं बहुत खुश हूँ") usually comes out as "neutral".

This file is a simple, explainable translator: a dictionary of common
emotional words. If the text looks like Hinglish or Hindi, known words are
swapped for English ones and the rest are kept. The model then reads the
translated text, and ORBIT shows the user what it understood.

It is deliberately simple (word-by-word), so it can miss meaning. That
limitation is measured honestly on the AI Lab page.
"""
import re

PHRASES = {
    "dil toot gaya": "my heart is broken",
    "dil toot": "heartbroken",
    "mann nahi": "i don't feel like it",
    "man nahi": "i don't feel like it",
    "samajh nahi": "i don't understand",
    "kuch samajh nahi": "i don't understand anything",
    "darr lag raha": "i am scared",
    "dar lag raha": "i am scared",
    "dar lagta": "i get scared",
    "yaad aa raha": "i miss",
    "yaad aa rahi": "i miss",
    "yaad aata": "i miss",
    "ro raha": "crying",
    "ro rahi": "crying",
    "lag raha hai": "feels",
    "lag rahi hai": "feels",
    "ho gaya": "happened",
    "ho gayi": "happened",
    "koi nahi": "nobody",
    "bilkul nahi": "not at all",
    "gussa aa raha": "i am angry",
    "gussa aa rahi": "i am angry",
    "gussa aata": "i get angry",
    "rona aa raha": "i want to cry",
    "rona aa rahi": "i want to cry",
    "neend nahi": "i can't sleep",
    "mood off": "upset",
    "mood kharab": "in a bad mood",
    "bore ho": "bored",
    "maza aa raha": "i am having fun",
    "maza aa gaya": "that was so much fun",
    "समझ नहीं": "i don't understand",
    "डर लग रहा": "i am scared",
    "गुस्सा आ रहा": "i am angry",
    "याद आ रही": "i miss",
    "याद आ रहा": "i miss",
}

WORDS = {
    "khush": "happy", "khushi": "happiness", "mast": "great", "maza": "fun", "mazaa": "fun",
    "udaas": "sad", "udas": "sad", "udaasi": "sadness", "dukhi": "unhappy", "dukh": "sorrow",
    "rona": "crying", "roya": "cried", "royi": "cried",
    "gussa": "angry", "gusse": "angry", "naraz": "upset", "naraaz": "upset", "chidh": "irritated",
    "pareshan": "worried", "pareshaan": "worried", "chinta": "worry", "tension": "stress",
    "dar": "fear", "darr": "fear", "darta": "afraid", "darti": "afraid", "ghabrahat": "anxiety",
    "ghabra": "anxious", "ghabrayi": "anxious", "ghabraya": "anxious",
    "akela": "alone", "akeli": "alone", "akelapan": "loneliness",
    "thaka": "tired", "thaki": "tired", "thakaan": "exhaustion", "thak": "tired",
    "pyaar": "love", "pyar": "love", "yaad": "miss", "shukriya": "thank you", "dhanyavad": "thank you",
    "garv": "proud", "umeed": "hope", "sharm": "embarrassed", "sharam": "embarrassed",
    "sharminda": "ashamed", "hairaan": "surprised", "hairan": "surprised",
    "bekar": "useless", "bekaar": "useless", "nafrat": "hate", "jalan": "jealousy",
    "sukoon": "peace", "sukun": "peace", "shaant": "calm", "shant": "calm",
    "accha": "good", "acha": "good", "achha": "good", "bura": "bad", "bure": "bad", "kharab": "bad",
    "pagal": "crazy", "boring": "boring",
    "bahut": "very", "bohot": "very", "bohut": "very", "zyada": "too much", "jyada": "too much",
    "bilkul": "completely", "thoda": "a little", "kam": "less", "sach": "really",
    "nahi": "not", "nahin": "not", "nhi": "not", "mat": "don't",
    "hai": "", "hain": "", "hu": "am", "hoon": "am", "hun": "am", "tha": "was", "thi": "was",
    "aa": "", "gaya": "", "gayi": "",
    "mujhe": "i", "mujhko": "me", "mai": "i", "mera": "my", "meri": "my", "mere": "my",
    "aaj": "today", "kal": "yesterday", "yaar": "friend", "dost": "friend", "ghar": "home",
    "padhai": "studies", "sab": "everything", "kuch": "something", "koi": "someone",
    "kyun": "why", "kya": "what", "chahiye": "need", "chahta": "want", "chahti": "want",
    "lag": "feel", "lagta": "feel", "lagti": "feel", "raha": "", "rahi": "", "rahe": "",
    "ko": "", "ki": "", "ka": "", "ke": "", "se": "", "toh": "", "to": "to", "bhi": "also",
    "खुश": "happy", "खुशी": "happiness", "दुखी": "sad", "उदास": "sad", "गुस्सा": "angry",
    "डर": "fear", "अकेला": "alone", "अकेली": "alone", "थका": "tired", "थकी": "tired",
    "बहुत": "very", "अच्छा": "good", "बुरा": "bad", "प्यार": "love", "याद": "miss",
    "परेशान": "worried", "चिंता": "worry", "तनाव": "stress", "शर्म": "embarrassed",
    "रोना": "crying", "मैं": "i", "मुझे": "i", "मेरा": "my", "मेरी": "my", "आज": "today",
    "नहीं": "not", "है": "", "हूँ": "am", "हूं": "am", "था": "was", "थी": "was",
    "माँ": "mother", "मां": "mother", "पापा": "father", "दोस्त": "friend", "परीक्षा": "exam",
    "कल": "tomorrow", "स्कूल": "school", "अपनी": "my", "से": "", "को": "", "कुछ": "anything",
}

MARKERS = {
    "hai", "hain", "nahi", "nahin", "nhi", "bahut", "bohot", "mujhe", "mera", "meri", "yaar",
    "kya", "kyun", "aaj", "raha", "rahi", "hoon", "hu", "tha", "thi", "kuch", "sab", "accha",
    "acha", "khush", "udaas", "gussa", "pareshan", "akela", "thaka", "pyaar", "lag", "lagta",
    "shukriya", "tum", "hamesha", "bhai", "kaise", "yeh", "jaana", "karun", "khaya", "dosto",
}

DEVANAGARI = re.compile(r"[ऀ-ॿ]")


def looks_hinglish(text):
    """True if the text seems to be Hinglish or Hindi rather than English."""
    if DEVANAGARI.search(text):
        return True
    words = re.findall(r"[a-z]+", text.lower())
    return sum(word in MARKERS for word in words) >= 2


def to_english(text):
    """Translate known Hinglish/Hindi words to English, word by word.

    Returns (text_for_the_model, was_translated).
    """
    if not looks_hinglish(text):
        return text, False

    result = text.lower()
    for phrase, english in sorted(PHRASES.items(), key=lambda pair: -len(pair[0])):
        result = re.sub(rf"(?<!\w){re.escape(phrase)}(?!\w)", english, result)

    words = re.findall(r"[^\s.,!?।]+|[.,!?]", result)
    translated = [WORDS.get(word, word) for word in words]
    english = " ".join(word for word in translated if word)
    english = re.sub(r"\s+([.,!?])", r"\1", english)
    return english, True
