# Hospital Review Sentiment Analysis - Backend

Python Flask backend with NLP sentiment analysis using Hugging Face Transformers.

## Setup

1. Create conda environment:
```bash
conda create -n hospital-review python=3.11 -y
conda activate hospital-review
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

## Re-analyzing Existing Reviews

### Method 1: Command Line Script (Recommended)
Run the standalone script to re-analyze all reviews with progress tracking and backup:

```bash
conda activate hospital-review
python reanalyze_reviews.py
```

This will:
- Create automatic backup of your reviews
- Show real-time progress updates
- Display sentiment statistics after completion
- Update all reviews with fresh NLP analysis

### Method 2: API Endpoint
Call the API endpoint while the server is running:

```bash
curl -X POST http://localhost:5000/api/reanalyze-all
```

Or use any HTTP client (Postman, Thunder Client, etc.) to send a POST request to:
```
POST http://localhost:5000/api/reanalyze-all
```

## API Endpoints

- GET /api/reviews - Get all reviews
- POST /api/reviews - Create new review with analysis
- POST /api/analyze - Analyze text without saving
- POST /api/reanalyze-all - Re-analyze all existing reviews (updates reviews.json)