from bz2 import BZ2File
from collections import defaultdict
from flask import Flask, request, jsonify, render_template, g
import json
import os

app = Flask('paste')

name = os.path.join(os.path.dirname(__file__), 'dict.json.bz2')
with BZ2File(name) as f:
    dictionary = json.load(f)

words = sorted(k for k in dictionary.keys())

def find_words(query):
    if not query:
        return {'data': []}

    results0 = []
    results1 = []
    results2 = []

    query = query.lower()
    for word in words:
        desc = dictionary[word]
        if query in word.lower():
            results0.append((word, desc))
        else:
            tmp = word.lower()
            for c in query:
                if c in tmp:
                    tmp = tmp.split(c, 1)[1]
                else:
                    break
            else:
                results1.append((word, desc))
                continue

            if query in desc:
                results2.append((word, desc))

    results0.sort(key=lambda x: (x[0].lower().index(query.lower()), x[0].lower()))
    return {'data': results0[:20] + results1[:20] + results2[:20]}

@app.route('/webster', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def slash():
    words = None
    query = (request.args.get('q') or request.form.get('query')) or ''
    if query:
        words = find_words(query)
    return render_template('index.html', words=words, query=query)

@app.route('/webster/search', methods=['POST'])
@app.route('/search', methods=['POST'])
def search():
    query = request.json['query']
    return jsonify(find_words(query))

if __name__ == '__main__':
    app.run(port=5006, debug=True)
