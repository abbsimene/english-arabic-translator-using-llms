"""
translator.py
-------------
Sends preprocessed sentences to Ollama (aya model)
and returns the translated text.

Uses prompt engineering to:
  - Specify the model's role as a professional translator
  - Handle scientific / AI-related vocabulary correctly
  - Ensure clean output (translation only, no explanations)
"""

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL      = "aya"

# ── Prompts ────────────────────────────────────────────────────────
# Prompt engineering: we give the model a clear role and strict
# instructions so it produces reliable, contextual translations
# especially for scientific and AI-related content.

PROMPTS = {
    "ar_to_en": (
        "You are a professional translator specialized in Arabic to English translation, "
        "including scientific and technical texts related to artificial intelligence and NLP. "
        "Translate the following Arabic text into fluent, accurate English. "
        "Preserve all technical terms exactly as they are. "
        "Return only the translation — no explanations, no notes, no extra text.\n\n"
        "Arabic: {text}\n"
        "English:"
    ),
    "en_to_ar": (
        "You are a professional translator specialized in English to Arabic translation, "
        "including scientific and technical texts related to artificial intelligence and NLP. "
        "Translate the following English text into fluent, accurate Modern Standard Arabic. "
        "Preserve all technical terms exactly as they are. "
        "Return only the translation — no explanations, no notes, no extra text.\n\n"
        "English: {text}\n"
        "Arabic:"
    ),
}


# ── Core translation function ──────────────────────────────────────

def translate_sentence(sentence: str, direction: str) -> str | None:
    """
    Send a single sentence to the Ollama API and return the translation.

    Args:
        sentence  : one clean sentence to translate
        direction : "ar_to_en" or "en_to_ar"

    Returns:
        translated string, or None if the request failed
    """
    prompt  = PROMPTS[direction].format(text=sentence)
    payload = {
        "model":  MODEL,
        "prompt": prompt,
        "stream": False,
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "").strip()

    except requests.exceptions.ConnectionError:
        print("\n  [ERROR] Cannot reach Ollama.")
        print("  Make sure Ollama is running: ollama serve")
        return None

    except requests.exceptions.Timeout:
        print("\n  [ERROR] Ollama request timed out.")
        return None

    except Exception as e:
        print(f"\n  [ERROR] Unexpected error: {e}")
        return None


# ── Translate a list of sentences ──────────────────────────────────

def translate(sentences: list, direction: str) -> str | None:
    """
    Translate a list of sentences one by one and join the results.

    Args:
        sentences : list of preprocessed sentences
        direction : "ar_to_en" or "en_to_ar"

    Returns:
        full translated text as a single string
    """
    results = []
    total   = len(sentences)

    for i, sentence in enumerate(sentences, 1):
        print(f"  Translating sentence {i}/{total}...", end="\r")
        result = translate_sentence(sentence, direction)
        if result:
            results.append(result)
        else:
            print(f"\n  [WARNING] Sentence {i} failed, skipping.")

    print(" " * 45, end="\r")  # clear progress line

    if not results:
        return None

    return " ".join(results)