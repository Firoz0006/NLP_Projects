from flask import Flask, render_template, request
import pandas as pd
import textdistance
import re
from collections import Counter
import os  # <-- Added for path handling

app = Flask(__name__)

# ------------------------------------------
# Load data with corrected path
# ------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "autocorrect_book.txt")  # Renamed file

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read().lower()
        words = re.findall(r'\w+', data)
except FileNotFoundError:
    raise SystemExit(f"Error: File '{file_path}' not found!")

# ------------------------------------------
word_freq = Counter(words)
total_words = sum(word_freq.values())
probs = {word: count/total_words for word, count in word_freq.items()}
# ------------------------------------------

@app.route('/')
def index():
    return render_template('index.html', suggestions=None)

@app.route('/suggest', methods=['POST'])
def suggest():
    keyword = request.form['keyword'].strip().lower()
    
    if not keyword:
        return render_template('index.html', suggestions=None)
    
    if keyword in probs:
        return render_template('index.html', 
                        message=f"'{keyword}' is already correct!",
                        suggestions=None)
    
    # Calculate similarities
    lev = textdistance.Levenshtein()
    similarities = [lev.normalized_similarity(keyword, word) for word in word_freq.keys()]
    
    df = pd.DataFrame({
        'Word': list(word_freq.keys()),
        'Probability': [probs[word] for word in word_freq.keys()],
        'Similarity': similarities
    })
    
    suggestions = df.sort_values(['Similarity', 'Probability'], ascending=False).head(10)
    return render_template('index.html', suggestions=suggestions.to_dict('records'))

if __name__ == '__main__':
    app.run(debug=True)