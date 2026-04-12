from flask import Flask, request, jsonify, render_template
from arabic_preprocessor  import preprocess_arabic,  detect_arabic
from english_preprocessor import preprocess_english
from LLMS                  import translate
from evaluator             import evaluate, auto_score

app     = Flask(__name__)
history = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/translate', methods=['POST'])
def translate_route():
    data      = request.json
    text      = data.get('text', '').strip()
    direction = data.get('direction', 'auto')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    if direction == 'auto':
        direction = 'ar_to_en' if detect_arabic(text) else 'en_to_ar'

    sentences = preprocess_arabic(text) if direction == 'ar_to_en' else preprocess_english(text)
    result    = translate(sentences, direction)

    if not result:
        return jsonify({'error': 'Translation failed'}), 500

    # auto score immediately
    quality = auto_score(text, result)

    history.append({'source': text, 'translation': result, 'direction': direction})
    return jsonify({
        'translation': result,
        'direction':   direction,
        'sentences':   len(sentences),
        'auto_score':  quality,
    })


@app.route('/evaluate', methods=['POST'])
def evaluate_route():
    data       = request.json
    reference  = data.get('reference', '').strip()
    hypothesis = data.get('hypothesis', '').strip()

    if not reference or not hypothesis:
        return jsonify({'error': 'Both fields required'}), 400

    return jsonify(evaluate(reference, hypothesis))


if __name__ == '__main__':
    app.run(debug=True)