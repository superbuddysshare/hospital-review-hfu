"""
Model Evaluation Script
Compares analyzer predictions against hospital.csv dataset labels
Uses: ensemble sentiment pipeline with derived star rating vote
Outputs: accuracy metrics, confusion matrix, precision/recall/F1
"""
import os
import argparse
import pandas as pd
from datetime import datetime
import json
from nlp_analyzer import analyze_review, preprocess_review, set_analysis_mode, get_analysis_mode

def load_original_dataset(csv_path='original_dataset/hospital.csv'):
    """Load the original doctor reviews dataset"""
    try:
        df = pd.read_csv(csv_path)
        print(f"✓ Loaded {len(df)} reviews from {csv_path}")
        return df
    except FileNotFoundError:
        print(f"❌ Error: {csv_path} not found!")
        return None

def normalize_sentiment(sentiment_value):
    """
    Normalize sentiment labels to consistent format
    Handles: 0/1, positive/negative, pos/neg, etc.
    """
    if isinstance(sentiment_value, (int, float)):
        # Binary: 0 = negative, 1 = positive
        return 'positive' if sentiment_value == 1 else 'negative'
    
    sentiment_str = str(sentiment_value).lower().strip()
    if sentiment_str in ['positive', 'pos', '1', 'good']:
        return 'positive'
    elif sentiment_str in ['negative', 'neg', '0', 'bad']:
        return 'negative'
    else:
        # Binary model: no mixed/neutral
        return sentiment_str

def evaluate_model(df):
    """
    Evaluate improved model predictions against original labels
    """
    print("\n" + "="*60)
    print("Starting Improved Model Evaluation")
    print("="*60)
    
    results = {
        'total': len(df),
        'correct': 0,
        'incorrect': 0,
        'confusion_matrix': {
            'true_positive': 0,  # Correctly predicted positive
            'true_negative': 0,  # Correctly predicted negative
            'false_positive': 0, # Predicted positive, actually negative
            'false_negative': 0, # Predicted negative, actually positive
        },
        'errors': []
    }
    
    # Determine column names (flexible for different CSV formats)
    review_col = None
    sentiment_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if col_lower in ['reviews', 'feedback', 'review', 'text', 'comment', 'review_text']:
            review_col = col
        elif col_lower in ['labels', 'sentiment label', 'sentiment', 'label', 'sentiment_label']:
            sentiment_col = col
    
    # Fallback: exact match for doctorReviews.csv
    if not review_col and 'reviews' in df.columns:
        review_col = 'reviews'
    if not sentiment_col and 'labels' in df.columns:
        sentiment_col = 'labels'
    
    if not review_col or not sentiment_col:
        print("❌ Error: Could not find review text and sentiment columns")
        print(f"Available columns: {list(df.columns)}")
        return None
    
    print(f"\nUsing columns:")
    print(f"  • Review: {review_col}")
    print(f"  • Sentiment: {sentiment_col}")
    
    print(f"\n🔄 Processing {len(df)} reviews with improved analyzer...")
    
    # Optional paraphrase logging for analysis
    paraphrase_log = os.environ.get("PARAPHRASE_LOG")

    for idx, row in df.iterrows():
        try:
            # Progress indicator
            if (idx + 1) % 25 == 0 or idx + 1 == len(df):
                print(f"  Progress: {idx + 1}/{len(df)} ({(idx + 1)/len(df)*100:.1f}%)")
            
            review_text = str(row[review_col])
            original_sentiment = normalize_sentiment(row[sentiment_col])
            
            # Skip empty reviews
            if not review_text or len(review_text.strip()) < 5:
                continue
            
            # Get model prediction using improved analyzer
            preprocessed = preprocess_review(review_text)
            prediction = analyze_review(review_text)
            predicted_sentiment = prediction['sentiment']

            if paraphrase_log:
                try:
                    entry = {
                        'index': int(idx),
                        'original': review_text,
                        'preprocessed': preprocessed,
                    }
                    with open(paraphrase_log, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                except Exception:
                    pass
            
            # Compare predictions (binary: positive/negative only)
            if predicted_sentiment == original_sentiment:
                results['correct'] += 1
                
                # Update confusion matrix
                if predicted_sentiment == 'positive':
                    results['confusion_matrix']['true_positive'] += 1
                elif predicted_sentiment == 'negative':
                    results['confusion_matrix']['true_negative'] += 1
            else:
                results['incorrect'] += 1
                
                # Update confusion matrix
                if predicted_sentiment == 'positive' and original_sentiment == 'negative':
                    results['confusion_matrix']['false_positive'] += 1
                elif predicted_sentiment == 'negative' and original_sentiment == 'positive':
                    results['confusion_matrix']['false_negative'] += 1
                
                # Store error details
                if len(results['errors']) < 20:  # Keep first 20 errors for analysis
                    results['errors'].append({
                        'index': idx,
                        'review': review_text[:100] + '...' if len(review_text) > 100 else review_text,
                        'full_review': review_text,  # Store full review for debugging
                        'preprocessed': preprocessed,
                        'original_sentiment': original_sentiment,
                        'predicted_sentiment': predicted_sentiment,
                        'confidence': prediction['score'],
                    })
        
        except Exception as e:
            print(f"  ⚠ Error processing review {idx}: {str(e)}")
            continue
    
    return results

def print_results(results):
    """Print evaluation results"""
    print("\n" + "="*60)
    print("Improved Model Evaluation Results")
    print("="*60)
    
    total = results['total']
    correct = results['correct']
    incorrect = results['incorrect']
    accuracy = (correct / total * 100) if total > 0 else 0
    
    print(f"\n📊 Overall Performance:")
    print(f"  • Total Reviews: {total}")
    print(f"  • Correct Predictions: {correct}")
    print(f"  • Incorrect Predictions: {incorrect}")
    print(f"  • Accuracy: {accuracy:.2f}%")
    
    cm = results['confusion_matrix']
    tp = cm['true_positive']
    tn = cm['true_negative']
    fp = cm['false_positive']
    fn = cm['false_negative']
    
    print(f"\n📈 Confusion Matrix:")
    print(f"                    Predicted")
    print(f"                Positive  Negative")
    print(f"  Actual Positive    {tp:4d}      {fn:4d}")
    print(f"  Actual Negative    {fp:4d}      {tn:4d}")
    
    # Calculate additional metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"\n📐 Detailed Metrics:")
    print(f"  • Precision: {precision:.2%} (of predicted positives, how many were correct)")
    print(f"  • Recall: {recall:.2%} (of actual positives, how many were found)")
    print(f"  • F1 Score: {f1_score:.2%} (harmonic mean of precision and recall)")
    
    if results['errors']:
        print(f"\n❌ Sample Misclassifications (first {len(results['errors'])}):")
        for i, error in enumerate(results['errors'][:10], 1):
            print(f"\n  {i}. Review: {error['review']}")
            print(f"     Preprocessed: {error.get('preprocessed', 'N/A')}")
            print(f"     Original: {error['original_sentiment']}")
            print(f"     Predicted: {error['predicted_sentiment']} (confidence: {error.get('confidence', 'N/A')})")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"evaluation_results_improved_{timestamp}.json"
    
    # Remove full_review from saved results to keep file size manageable
    results_to_save = results.copy()
    results_to_save['errors'] = [
        {k: v for k, v in error.items() if k != 'full_review'}
        for error in results['errors']
    ]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results_to_save, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Full results saved to: {output_file}")

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description="Evaluate the analyzer against the hospital dataset")
        parser.add_argument('--mode', choices=['combined', 'binary', 'star'], help='Analysis mode to use for this run')
        args = parser.parse_args()

        selected_mode = args.mode or os.environ.get('ANALYSIS_MODE', 'combined')
        active_mode = set_analysis_mode(selected_mode)

        print("="*60)
        print("Hospital Review Model Evaluation - Improved Version")
        print("="*60)
        print(f"Using analysis mode: {active_mode}")
        print()
        
        # Load dataset
        print("Loading dataset...")
        df = load_original_dataset('original_dataset/hospital.csv')
        
        if df is not None:
            print(f"Dataset loaded successfully with {len(df)} rows")
            # Evaluate model
            print("Starting evaluation...")
            results = evaluate_model(df)
            
            if results:
                # Print results
                print_results(results)
            else:
                print("\n❌ Evaluation failed.")
        else:
            print("\n❌ Could not load dataset.")
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
