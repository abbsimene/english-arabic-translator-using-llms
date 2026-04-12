import sacrebleu
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)


def evaluate(reference: str, hypothesis: str) -> dict:
    bleu       = sacrebleu.corpus_bleu([hypothesis], [[reference]])
    bleu_score = round(bleu.score, 2)
    return {"bleu": bleu_score, "label": interpret(bleu_score)}


def interpret(score: float) -> str:
    if score >= 50:   return "Excellent"
    elif score >= 30: return "Good"
    elif score >= 15: return "Acceptable"
    else:             return "Poor"


def auto_score(source: str, translation: str) -> dict:
    """
    Automatic quality estimate with no reference needed.
    Uses two signals:
      1. Length ratio — translation should not be drastically shorter/longer
      2. Token coverage — rough word count ratio
    Returns a percentage 0-100.
    """
    src_words = len(word_tokenize(source))
    trs_words = len(word_tokenize(translation))

    if src_words == 0:
        return {"score": 0, "label": "Poor"}

    ratio = trs_words / src_words

    # ideal ratio is between 0.7 and 1.5 (Arabic/English length difference)
    if 0.7 <= ratio <= 1.5:
        score = 90
    elif 0.5 <= ratio < 0.7 or 1.5 < ratio <= 2.0:
        score = 65
    elif 0.3 <= ratio < 0.5 or 2.0 < ratio <= 2.5:
        score = 40
    else:
        score = 20

    return {"score": score, "label": interpret_auto(score)}


def interpret_auto(score: float) -> str:
    if score >= 80: return "Good"
    elif score >= 55: return "Acceptable"
    else:           return "Poor"