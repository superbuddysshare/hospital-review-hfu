from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
from nlp_analyzer import analyze_review
import os

app = Flask(__name__)
CORS(app)

REVIEWS_FILE = 'reviews.json'

def load_reviews():
    if os.path.exists(REVIEWS_FILE):
        with open(REVIEWS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_reviews(reviews):
    with open(REVIEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False)

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    reviews = load_reviews()
    return jsonify(reviews)

@app.route('/api/reviews', methods=['POST'])
def create_review():
    data = request.json
    reviews = load_reviews()
    
    new_id = max([r['id'] for r in reviews], default=0) + 1
    analysis = analyze_review(data['review_text'])
    
    new_review = {
        'id': new_id,
        'hospital_id': data.get('hospital_id', f'H{new_id:03d}'),
        'hospital_name': data['hospital_name'],
        'hospital_address': data.get('hospital_address', ''),
        'review_text': data['review_text'],
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'overall_sentiment': analysis['sentiment'],
        'sentiment_score': analysis['score'],
        'aspects': analysis['aspects']
    }
    
    reviews.append(new_review)
    save_reviews(reviews)
    
    return jsonify(new_review), 201

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    data = request.json
    analysis = analyze_review(data['text'])
    return jsonify(analysis)

if __name__ == '__main__':
    app.run(debug=True, port=5000)