"""
Script to re-analyze all existing reviews with updated sentiment analysis
Uses improved analysis with:
  • siebert/sentiment-roberta-large-english (binary: positive/negative, 93.2% accuracy)
  • Trained on 15 diverse review datasets (Amazon, Yelp, Twitter, etc.)
  • Domain-specific sentiment corrections for medical/hospital context
  • Negation handling (e.g., "not good" → negative, "not bad" → positive)
  • Windowed aspect sentiment to reduce cross-clause interference
  • nlptown for 1-5 star rating inference
    • Preprocessing: grammar fixes, URL/noise stripping, contraction expansion, lowercasing, stopword removal
Usage: python reanalyze_reviews.py
"""
import json
import os
from nlp_analyzer import analyze_review
from datetime import datetime

REVIEWS_FILE = 'reviews.json'
BACKUP_DIR = 'backups'
BACKUP_FILE = os.path.join(BACKUP_DIR, f'reviews_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')

def reanalyze_all_reviews():
    """Re-analyze all reviews and update with new sentiment scores and aspects"""
    
    # Check if reviews file exists
    if not os.path.exists(REVIEWS_FILE):
        print(f"❌ Error: {REVIEWS_FILE} not found!")
        return
    
    # Load existing reviews
    print(f"📖 Loading reviews from {REVIEWS_FILE}...")
    with open(REVIEWS_FILE, 'r', encoding='utf-8') as f:
        reviews = json.load(f)
    
    print(f"✓ Found {len(reviews)} reviews to analyze")
    
    # Create backup
    print(f"� Creating backup: {BACKUP_FILE}...")
    os.makedirs(BACKUP_DIR, exist_ok=True)
    with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False)
    print(f"✓ Backup saved")
    
    # Re-analyze each review
    print(f"\n🔄 Starting re-analysis...")
    updated_count = 0
    
    for idx, review in enumerate(reviews, 1):
        try:
            # Show progress
            if idx % 50 == 0 or idx == len(reviews):
                print(f"  Progress: {idx}/{len(reviews)} ({(idx/len(reviews)*100):.1f}%)")
            
            # Get review text
            review_text = review.get('review_text', '')
            if not review_text:
                print(f"  ⚠ Skipping review {review['id']}: No review text")
                continue
            
            # Run analysis
            analysis = analyze_review(review_text)
            
            # Update review with new analysis
            review['overall_sentiment'] = analysis['sentiment']
            review['sentiment_score'] = analysis['score']
            review['star_rating'] = analysis.get('star_rating', 3)
            review['aspects'] = analysis['aspects']
            
            updated_count += 1
            
        except Exception as e:
            print(f"  ❌ Error analyzing review {review['id']}: {str(e)}")
            continue
    
    # Save updated reviews
    print(f"\n💾 Saving updated reviews to {REVIEWS_FILE}...")
    with open(REVIEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Complete!")
    print(f"  • Total reviews: {len(reviews)}")
    print(f"  • Successfully updated: {updated_count}")
    print(f"  • Backup saved as: {BACKUP_FILE}")
    
    # Show some statistics (binary sentiment: positive/negative only)
    positive = sum(1 for r in reviews if r.get('overall_sentiment') == 'positive')
    negative = sum(1 for r in reviews if r.get('overall_sentiment') == 'negative')
    
    print(f"\n📊 Sentiment Distribution:")
    print(f"  • Positive: {positive} ({positive/len(reviews)*100:.1f}%)")
    print(f"  • Negative: {negative} ({negative/len(reviews)*100:.1f}%)")
    
    # Show average star rating if available
    star_ratings = [r.get('star_rating') for r in reviews if r.get('star_rating')]
    if star_ratings:
        avg_stars = sum(star_ratings) / len(star_ratings)
        print(f"\n⭐ Average Star Rating: {avg_stars:.2f}/5.0")

if __name__ == '__main__':
    print("=" * 60)
    print("Hospital Review Re-Analysis Tool")
    print("=" * 60)
    print()
    
    # Confirm action
    response = input("⚠️  This will update all reviews. Continue? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        print()
        reanalyze_all_reviews()
    else:
        print("\n❌ Cancelled.")
