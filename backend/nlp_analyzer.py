from transformers import pipeline
import re

# Star rating model that outputs 1-5 stars directly
star_rating_analyzer = pipeline(
    "text-classification",
    model="nlptown/bert-base-multilingual-uncased-sentiment"
)

ASPECT_KEYWORDS = {
    'staff': ['staff', 'doctor', 'nurse', 'personnel', 'employee', 'professional', 'receptionist'],
    'equipment': ['equipment', 'machine', 'technology', 'modern', 'facility', 'tool'],
    'wait_time': ['wait', 'waiting', 'delay', 'time', 'queue', 'hours'],
    'cleanliness': ['clean', 'dirty', 'hygiene', 'sanitary', 'tidy', 'messy'],
    'insurance': ['insurance', 'coverage', 'billing', 'payment', 'cost', 'expensive'],
    'treatment': ['treatment', 'care', 'diagnosis', 'therapy', 'medicine', 'prescription']
}

def analyze_review(text):
    """
    Analyze review sentiment and return 1-5 star rating
    
    Returns:
        {
            'sentiment': 'positive' or 'negative',
            'score': confidence score,
            'star_rating': 1-5 stars,
            'aspects': list of detected aspects with ratings
        }
    """
    # Get star rating from model
    result = star_rating_analyzer(text[:512])[0]
    star_rating = int(result['label'].split()[0])  # Extract number from "5 stars"
    confidence = result['score']
    
    # Determine binary sentiment from stars
    sentiment = 'positive' if star_rating >= 3 else 'negative'
    
    return {
        'sentiment': sentiment,
        'score': round(confidence, 2),
        'star_rating': star_rating,
        'aspects': extract_aspects(text)
    }

def extract_aspects(text):
    """Extract healthcare aspects and their sentiments with star ratings"""
    found_aspects = []
    sentences = re.split(r'[.!?]', text)
    
    for aspect_name, keywords in ASPECT_KEYWORDS.items():
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            if any(keyword in sentence_lower for keyword in keywords):
                if len(sentence.strip()) > 5:
                    try:
                        result = star_rating_analyzer(sentence[:512])[0]
                        star_rating = int(result['label'].split()[0])
                        sentiment = 'positive' if star_rating >= 3 else 'negative'
                        
                        found_aspects.append({
                            'aspect': aspect_name,
                            'sentiment': sentiment,
                            'star_rating': star_rating,
                            'score': round(result['score'], 2)
                        })
                        break
                    except:
                        pass
    
    return found_aspects
