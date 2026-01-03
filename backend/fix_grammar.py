"""
Fix grammar and spelling in review texts
"""
import json
import re


def fix_grammar(text):
    """Fix grammar and spelling with deterministic rules (no ML rewriting)"""
    
    # Fix spacing and punctuation
    text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between concatenated words
    text = re.sub(r'([a-zA-Z])([,;:.!?])([A-Za-z])', r'\1\2 \3', text)  # Space after punctuation
    text = re.sub(r'([.!?])(?=[A-Za-z])', r'\1 ', text)  # Space after sentence end
    text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)  # Split letters and digits
    text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)
    
    # Common spelling/grammar fixes
    fixes = {
        r'\bavilable\b': 'available',
        r'\bremondening\b': 'recommending',
        r'\bremonding\b': 'recommending',
        r'\batleast\b': 'at least',
        r'\brecomended\b': 'recommended',
        r'\bdefined\b': 'defined',
        r'\bdried\b': 'tried',
        r'\bdyed\b': 'said',
        r'\bmobnumber\b': 'mobile number',
        r'\bgty\b': 'city',
        r'\beffected\b': 'affected',
        r'\bacurate\b': 'accurate',
        r'\bfrankly\btalking\b': 'frankly speaking,',
        r'\bfranklytalking\b': 'frankly speaking,',
        r'\bsitings\b': 'sittings',
        r'\blaringitis\b': 'laryngitis',
        r'\bspecialist\bin\sapollo\b': 'specialist at Apollo',
        r'\bwiest\b': 'west',
        r'\bremonded\b': 'recommended',
        r'\bsomes\b': 'some',
        r'\bmedicines\s*the\s*estimation': 'medicines. The estimation',
        r'\bmedicinesthe\b': 'medicines. The',
    }
    
    for pattern, replacement in fixes.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Fix basic contractions and pronouns
    text = re.sub(r'\bi am\b', 'I am', text, flags=re.IGNORECASE)
    text = re.sub(r'\bi m\b', "I'm", text, flags=re.IGNORECASE)
    text = re.sub(r'\bi have been having\b', 'I have had', text, flags=re.IGNORECASE)
    text = re.sub(r'\bmy self\b', 'myself', text, flags=re.IGNORECASE)
    text = re.sub(r'\bwasn\'t advised\b', 'was not advised', text, flags=re.IGNORECASE)
    text = re.sub(r'\bdidn\'t gave\b', 'did not give', text, flags=re.IGNORECASE)
    text = re.sub(r'\bwasn\'t\b', 'was not', text, flags=re.IGNORECASE)
    text = re.sub(r'\bdon\'t\b', 'do not', text, flags=re.IGNORECASE)
    text = re.sub(r'\bdoesn\'t\b', 'does not', text, flags=re.IGNORECASE)
    text = re.sub(r'\bdidn\'t\b', 'did not', text, flags=re.IGNORECASE)
    
    # Fix people/peoples
    text = re.sub(r'\bpeoples\b', 'people', text, flags=re.IGNORECASE)
    text = re.sub(r'\bfeelings of people\b', 'people\'s feelings', text, flags=re.IGNORECASE)
    
    # Fix run-on sentences - add periods and proper spacing
    text = re.sub(r'(\w)\s*(\w+)\s+and\s+the\s+(\w+)\s+was', r'\1. \2 and the \3 was', text)

    # Capitalize first letter and clean up
    if text:
        text = text[0].upper() + text[1:]
    
    # Final cleanup
    text = text.strip()
    text = re.sub(r'\s+([.,!?])', r'\1', text)  # Remove space before punctuation
    text = re.sub(r'([.!?])\s*([a-z])', lambda m: m.group(1) + ' ' + m.group(2).upper(), text)  # Capitalize after period
    
    return text

def process_reviews():
    """Process all reviews and fix grammar"""
    
    # Load reviews
    with open('reviews.json', 'r', encoding='utf-8') as f:
        reviews = json.load(f)
    
    print(f"Processing {len(reviews)} reviews...")
    
    for idx, review in enumerate(reviews, 1):
        original = review['review_text']
        fixed = fix_grammar(original)
        
        if original != fixed:
            review['review_text'] = fixed
            if idx <= 5:  # Show first few changes
                print(f"\nReview {idx}:")
                print(f"  Before: {original[:100]}...")
                print(f"  After:  {fixed[:100]}...")
    
    # Save fixed reviews
    with open('reviews.json', 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Fixed all {len(reviews)} reviews and saved to reviews.json")

if __name__ == '__main__':
    process_reviews()
