import os

from arabic_preprocessor  import preprocess_arabic,  detect_arabic
from english_preprocessor import preprocess_english, detect_english
from LLMS          import translate
from evaluator             import evaluate


BANNER = """
╔══════════════════════════════════════════════════════╗
║   Arabic  ↔  English  Translator                     ║
║   Model : Aya (Ollama)                               ║
╠══════════════════════════════════════════════════════╣
║  Commands:                                           ║
║    type text  →  auto-detect and translate           ║
║    file       →  load a .txt file                    ║
║    lang       →  manually set direction              ║
║    eval       →  BLEU score on last translation      ║
║    history    →  show past translations              ║
║    quit       →  exit                                ║
╚══════════════════════════════════════════════════════╝
"""

DIRECTIONS = {
    "1": ("ar_to_en", "Arabic → English"),
    "2": ("en_to_ar", "English → Arabic"),
}

history = []  # (source_text, translated_text, direction)


def choose_direction() -> tuple:
    print("\n  Select direction:")
    print("  1. Arabic → English")
    print("  2. English → Arabic")
    while True:
        choice = input("  Your choice (1/2): ").strip()
        if choice in DIRECTIONS:
            return DIRECTIONS[choice]
        print("  Please enter 1 or 2.")


def load_file() -> str | None:
    path = input("\n  Enter file path (.txt): ").strip()
    if not os.path.exists(path):
        print(f"  [ERROR] File not found: {path}")
        return None
    if not path.endswith(".txt"):
        print("  [ERROR] Only .txt files are supported.")
        return None
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"  Loaded {len(content)} characters from '{path}'")
    return content


def save_output(text: str, direction: str) -> None:
    filename = f"output_{direction}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"  Saved to '{filename}'")


def show_history() -> None:
    if not history:
        print("\n  No translations yet in this session.")
        return
    print(f"\n  {'─' * 50}")
    for i, (src, trs, direction) in enumerate(history, 1):
        label       = "AR → EN" if direction == "ar_to_en" else "EN → AR"
        src_preview = src[:70] + ("..." if len(src) > 70 else "")
        trs_preview = trs[:70] + ("..." if len(trs) > 70 else "")
        print(f"  [{i}]  {label}")
        print(f"  Source      : {src_preview}")
        print(f"  Translation : {trs_preview}")
        print(f"  {'─' * 50}")


def run_translation(text: str, direction: str) -> str | None:
    sentences = preprocess_arabic(text) if direction == "ar_to_en" else preprocess_english(text)
    print(f"\n  Preprocessing done: {len(sentences)} sentence(s) detected.")

    result = translate(sentences, direction)

    if result:
        print(f"\n  {'─' * 50}")
        print(f"  Translation:\n\n  {result}")
        print(f"\n  {'─' * 50}")
        history.append((text, result, direction))
        save = input("\n  Save output to file? (y/n): ").strip().lower()
        if save == "y":
            save_output(result, direction)
    else:
        print("\n  [ERROR] Translation failed. Is Ollama running?")
        print("  Run: ollama serve   (in a separate terminal)")

    return result


def run_evaluation() -> None:
    if not history:
        print("\n  No translations in history yet. Translate something first.")
        return
    print("\n  Paste a correct human reference translation to compare against.")
    reference = input("  Reference: ").strip()
    if not reference:
        print("  [ERROR] Reference cannot be empty.")
        return
    evaluate(reference, history[-1][1])


def run() -> None:
    print(BANNER)
    forced_direction = None

    while True:
        try:
            user_input = input("\nEnter text or command: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("\n  Goodbye!")
            break

        elif user_input.lower() == "history":
            show_history()

        elif user_input.lower() == "eval":
            run_evaluation()

        elif user_input.lower() == "lang":
            forced_direction, label = choose_direction()
            print(f"\n  Direction locked to: {label}")

        elif user_input.lower() == "file":
            text = load_file()
            if text:
                if forced_direction:
                    direction = forced_direction
                else:
                    direction = "ar_to_en" if detect_arabic(text) else "en_to_ar"
                    label     = "Arabic → English" if direction == "ar_to_en" else "English → Arabic"
                    print(f"  [Auto-detected: {label}]")
                run_translation(text, direction)

        else:
            if forced_direction:
                direction        = forced_direction
                forced_direction = None
            else:
                direction = "ar_to_en" if detect_arabic(user_input) else "en_to_ar"
                label     = "Arabic → English" if direction == "ar_to_en" else "English → Arabic"
                print(f"  [Auto-detected: {label}]")
            run_translation(user_input, direction)


if __name__ == "__main__":
    run()


