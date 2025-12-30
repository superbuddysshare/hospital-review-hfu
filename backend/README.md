# Hospital Review Sentiment Analysis - Backend

Python Flask backend with NLP sentiment analysis using Hugging Face Transformers.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run server:
```bash
python app.py
```

Server runs on http://localhost:5000

## API Endpoints

- GET /api/reviews - Get all reviews
- POST /api/reviews - Create new review with analysis
- POST /api/analyze - Analyze text without saving