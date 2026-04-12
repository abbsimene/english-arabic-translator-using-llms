import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"

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


def translate_sentence(sentence: str, direction: str) -> str | None:
    prompt = PROMPTS[direction].format(text=sentence)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"\n  [ERROR] Groq API error: {e}")
        return None


def translate(sentences: list, direction: str) -> str | None:
    results = []
    for sentence in sentences:
        result = translate_sentence(sentence, direction)
        if result:
            results.append(result)
    return " ".join(results) if results else None