import re
import nltk
from nltk.tokenize import sent_tokenize

nltk.download('punkt',     quiet=True)
nltk.download('punkt_tab', quiet=True)


# ── Normalization ──────────────────────────────────────────────────

def normalize(text: str) -> str:
    text = re.sub(r'<[^>]+>', ' ', text)                      # remove HTML
    text = re.sub(r'http\S+', '', text)                       # remove URLs
    text = re.sub("[إأآا]", "ا", text)                        # unify alef variants
    text = re.sub("ة", "ه", text)                             # unify teh marbuta
    text = re.sub(r'[\u064B-\u065F\u0617-\u061A]', '', text)  # remove tashkeel
    text = re.sub(r'\u0640', '', text)                         # remove tatweel
    text = re.sub(r'[^\u0600-\u06FF\s\.\،\؟\!]', '', text)   # keep Arabic + punctuation
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ── Tokenization ───────────────────────────────────────────────────

def tokenize(text: str) -> list:
    return sent_tokenize(text, language='arabic')


# ── Full pipeline ──────────────────────────────────────────────────

def preprocess_arabic(text: str) -> list:
    text = normalize(text)
    return tokenize(text)


# ── Language detection ─────────────────────────────────────────────

def detect_arabic(text: str) -> bool:
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    return arabic_chars > len(text) * 0.2