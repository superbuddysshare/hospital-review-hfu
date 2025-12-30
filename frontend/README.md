# HealthVoice - Hospital Review Platform

A modern hospital review platform with AI-powered sentiment analysis. Built with React (JavaScript), and Tailwind CSS, designed to connect with a Python Flask backend for review storage and sentiment analysis.

## Features

- 📊 **Real-time Sentiment Analysis** - AI-powered analysis of review text with positive/negative/neutral classification
- 🏥 **Hospital Reviews** - View and submit reviews for healthcare facilities
- 🎨 **Beautiful UI** - Modern, accessible interface with smooth animations
- 📱 **Responsive Design** - Works seamlessly on desktop and mobile devices
- 🔄 **Live Preview** - See sentiment analysis as you type your review
- 📈 **Community Insights** - Dashboard showing review statistics and sentiment distribution

## Backend API Requirements

This frontend expects a Flask backend with the following endpoints:

### GET /api/reviews
Returns all reviews as JSON array:
```json
[
  {
    "id": 1,
    "hospital_id": "H001",
    "hospital_name": "City General Hospital",
    "hospital_address": "123 Main St, City, State",
    "review_text": "Great experience with the staff...",
    "timestamp": "2024-01-15T10:30:00Z",
    "overall_sentiment": "positive",
    "sentiment_score": 0.85,
    "star_rating": 4,
    "aspects": [
      {
        "aspect": "staff",
        "sentiment": "positive",
        "score": 0.9,
        "star_rating": 5
      },
      {
        "aspect": "equipment",
        "sentiment": "positive",
        "score": 0.85,
        "star_rating": 4
      }
    ]
  }
]
```

### POST /api/reviews
Creates a new review with sentiment analysis. Expects:
```json
{
  "hospital_name": "City General Hospital",
  "hospital_address": "123 Main St, City, State",
  "review_text": "Great experience...",
  "hospital_id": "H001"
}
```

Returns the created review with analysis (same structure as GET).

### POST /api/analyze
Analyzes text without saving. Expects:
```json
{
  "text": "Review text to analyze..."
}
```

Returns analysis:
```json
{
  "sentiment": "positive",
  "score": 0.85,
  "aspects": [...]
}
```

## Setup

1. **Configure Backend URL**
   
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set your Flask backend URL:
   ```
   VITE_API_URL=http://localhost:5000
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```

4. **Ensure Backend is Running**
   
   Make sure your Flask backend is running and accessible at the URL specified in `.env`.

## Architecture

```
src/
├── components/
│   ├── ReviewCard.jsx        # Individual review display
│   ├── ReviewDialog.jsx      # Review submission form
│   ├── FilterBar.jsx         # Search and filter controls
│   ├── HospitalProfile.jsx   # Hospital profile page
│   ├── EmptyState.jsx        # No reviews placeholder
│   └── ui/                   # Shadcn UI components
├── lib/
│   ├── api.js                # Backend API service
│   ├── hospital-stats.js     # Hospital statistics aggregation
│   └── utils.js              # Utilities
├── hooks/
│   └── use-mobile.js         # Mobile detection hook
├── App.jsx                   # Main application
├── main.jsx                  # Application entry point
└── index.css                 # Custom theme & styles
```

## Technology Stack

- **React 19** - UI framework
- **JavaScript (ES6+)** - Modern JavaScript with JSX
- **Tailwind CSS** - Styling
- **Shadcn UI** - Component library
- **Framer Motion** - Animations
- **Phosphor Icons** - Icon set
- **Sonner** - Toast notifications
- **Vite** - Build tool

## Color Palette

The design uses a medical-inspired color palette:
- **Primary**: Deep Medical Blue - Trust and professionalism
- **Accent**: Warm Coral - Compassion and care
- **Positive**: Vibrant Green - Health and positive outcomes
- **Negative**: Soft Red - Concerns without aggression
- **Neutral**: Medium Gray - Balanced feedback

## Contributing

This is a frontend-only application designed to work with a Python Flask backend. Ensure your backend follows the API contract described above.

## License

See LICENSE file for details.
