import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.tokenize import word_tokenize

nltk.download('punkt',     quiet=True)
nltk.download('punkt_tab', quiet=True)


def compute_bleu(reference_text: str, hypothesis_text: str) -> float:
    smoothie          = SmoothingFunction().method1
    reference_tokens  = word_tokenize(reference_text.lower(),  language='english')
    hypothesis_tokens = word_tokenize(hypothesis_text.lower(), language='english')
    return sentence_bleu([reference_tokens], hypothesis_tokens, smoothing_function=smoothie)


def interpret_bleu(score: float) -> str:
    if score >= 0.5:
        return "Excellent"
    elif score >= 0.3:
        return "Good"
    elif score >= 0.15:
        return "Acceptable"
    else:
        return "Poor — consider refining the prompt"


def evaluate(reference_text: str, hypothesis_text: str) -> float:
    score = compute_bleu(reference_text, hypothesis_text)
    label = interpret_bleu(score)
    print(f"\n  {'─' * 40}")
    print(f"  BLEU Score  :  {score:.4f}")
    print(f"  Quality     :  {label}")
    print(f"  {'─' * 40}")
    return score