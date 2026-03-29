import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

nltk.download('punkt',     quiet=True)
nltk.download('punkt_tab', quiet=True)
 
 
CONTRACTIONS = {
    "don't": "do not", "doesn't": "does not", "didn't": "did not",
    "can't": "cannot", "won't": "will not", "isn't": "is not",
    "aren't": "are not", "wasn't": "was not", "weren't": "were not",
    "wouldn't": "would not", "couldn't": "could not", "shouldn't": "should not",
    "it's": "it is", "that's": "that is", "he's": "he is",
    "she's": "she is", "there's": "there is", "what's": "what is",
    "I'm": "I am", "I've": "I have", "I'll": "I will", "I'd": "I would",
    "you're": "you are", "they're": "they are", "we're": "we are",
    "let's": "let us", "could've": "could have", "should've": "should have",
}
 
ABBREVIATIONS = {
    r'\bDr\.':     'Doctor',
    r'\bMr\.':     'Mister',
    r'\bMrs\.':    'Missus',
    r'\bProf\.':   'Professor',
    r'\bDept\.':   'Department',
    r'\bapprox\.': 'approximately',
    r'\bvs\.':     'versus',
    r'\be\.g\.':   'for example',
    r'\bi\.e\.':   'that is',
    r'\betc\.':    'and so on',
}



# ── Normalization ──────────────────────────────────────────────────
 
def normalize(text: str) -> str:
    text = re.sub(r'<[^>]+>', ' ', text)              # remove HTML
    text = re.sub(r'http\S+', '', text)               # remove URLs
    text = re.sub(r'[^\w\s\.,!?;:\'\"-]', '', text)  # remove symbols
 
    for contraction, expansion in CONTRACTIONS.items():
        text = re.sub(re.escape(contraction), expansion, text, flags=re.IGNORECASE)
 
    for pattern, replacement in ABBREVIATIONS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
 
    text = re.sub(r'\s+', ' ', text).strip()
    return text
 
# ── Tokenization ───────────────────────────────────────────────────
 
def tokenize(text: str) -> list:
    return sent_tokenize(text, language='english')
 
 
# ── Full pipeline ──────────────────────────────────────────────────
 
def preprocess_english(text: str) -> list:
    text = normalize(text)
    return tokenize(text)
 
 
# ── Language detection ─────────────────────────────────────────────
 
def detect_english(text: str) -> bool:
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    return arabic_chars <= len(text) * 0.2
 