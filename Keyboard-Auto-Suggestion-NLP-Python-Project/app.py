from flask import Flask, render_template, request
import pandas as pd
import textdistance
import re
from collections import Counter

app = Flask(__name__)

# Load and preprocess words from the file
words = []
file_path = 'book.txt'  # Ensure the correct path

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read().lower()
        words = re.findall(r'\w+', data)  # Use raw string for regex
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found. Please check the path.")
    exit()

# Create word frequency dictionary
words_freq_dict = Counter(words)
Total = sum(words_freq_dict.values())

# Compute word probabilities
probs = {k: words_freq_dict[k] / Total for k in words_freq_dict.keys()}

@app.route('/')
def index():
    return render_template('index.html', suggestions=None)

@app.route('/suggest', methods=['POST'])
def suggest():
    keyword = request.form.get('keyword', '').strip().lower()
    
    if not keyword:  # Handle empty input
        return render_template('index.html', suggestions=None)

    # Compute similarity scores
    similarities = [1 - textdistance.Jaccard(qval=2).distance(v, keyword) for v in words_freq_dict.keys()]

    # Create DataFrame with words, probabilities, and similarity scores
    df = pd.DataFrame({'Word': list(words_freq_dict.keys()), 'Prob': list(probs.values()), 'Similarity': similarities})

    # Sort results by similarity and probability
    suggestions = df.sort_values(['Similarity', 'Prob'], ascending=False).head(10)[['Word', 'Similarity']]
    suggestions_list = suggestions.to_dict('records')  # Convert to list of dictionaries

    return render_template('index.html', suggestions=suggestions_list)

if __name__ == '__main__':
    app.run(debug=True)
