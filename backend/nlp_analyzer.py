from transformers import pipeline
import re
import emoji
import torch
import warnings

warnings.filterwarnings('ignore', message='.*sequentially on GPU.*')
warnings.filterwarnings('ignore', category=FutureWarning)

DEVICE = 0 if torch.cuda.is_available() else -1

# Unified model set: binary ensemble + star estimators for stability
star_rating_models = {
    'nlptown': pipeline(
        "text-classification",
        model="nlptown/bert-base-multilingual-uncased-sentiment",
        device=DEVICE,
    ),
    'setfit_sst5': pipeline(
        "text-classification",
        model="SetFit/distilbert-base-uncased__sst5__all-train",
        device=DEVICE,
    ),
}

binary_sentiment_models = {
    'roberta': pipeline(
        "sentiment-analysis",
        model="siebert/sentiment-roberta-large-english",
        device=DEVICE,
    ),
    'distilbert': pipeline(
        "text-classification",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        device=DEVICE,
    ),
}

POSITIVE_OUTCOME_TOKENS = {
    'treated', 'treat', 'improved', 'improve', 'fixed', 'resolve', 'resolved', 'better', 'ok', 'okay', 'fine', 'alright',
    'cured', 'recovered', 'healed', 'healing', 'recovery'
}


ASPECT_PROFILES = {
    'staff': {
        'keywords': {
            'staff', 'staffs', 'personnel', 'employees', 'frontdesk', 'front-desk', 'front', 'desk', 'reception',
            'receptionist', 'receptionists', 'coordinator', 'coordinators', 'management', 'admin', 'administration', 'team',
            'helpers', 'support', 'customer', 'care', 'ward', 'attendant', 'attendants'
        },
        'positive_terms': {'friendly', 'polite', 'helpful', 'supportive', 'cooperative', 'professional', 'attentive', 'courteous', 'respectful', 'responsive', 'kind', 'caring', 'swift', 'warm', 'humble', 'nice'},
        'negative_terms': {'rude', 'arrogant', 'dismissive', 'careless', 'unprofessional', 'hostile', 'unhelpful', 'irresponsible', 'apathetic', 'argumentative', 'lazy', 'slow', 'ignorant', 'harsh'},
        'positive_phrases': ['staff was very caring', 'support team', 'helpful staff', 'staff took good care', 'people working there', 'people were responsive', 'responding quickly'],
        'negative_phrases': ['lack of staff', 'no staff', 'under staffed', 'short staffed', 'rude staff', 'staff was not helpful', 'staff not helpful', 'not helpful though', 'not helpful but'],
        'negation_hooks': ['understaffed', 'under-staffed', 'shortstaffed', 'short-staffed'],
    },
    'cleanliness': {
        'keywords': {
            'clean', 'cleanliness', 'dirty', 'filthy', 'sanitary', 'hygiene', 'hygienic', 'messy', 'odor', 'smell', 'stench',
            'trash', 'garbage', 'washroom', 'washrooms', 'toilet', 'toilets', 'restroom', 'restrooms', 'bathroom', 'bathrooms',
            'ward', 'wards', 'bed', 'beds', 'linen', 'corridor', 'corridors', 'floor', 'floors', 'spill', 'spills'
        },
        'positive_terms': {'clean', 'spotless', 'sterile', 'fresh', 'tidy', 'immaculate', 'hygienic', 'sanitized', 'neat', 'well-kept', 'organized'},
        'negative_terms': {'dirty', 'gross', 'smelly', 'filthy', 'stained', 'sticky', 'unsanitary', 'nasty', 'stinky', 'unclean', 'foul', 'messy'},
        'positive_phrases': ['very clean', 'well maintained', 'neat and tidy', 'sparkling clean'],
        'negative_phrases': ['smelled bad', 'smelled awful', 'dirty wards', 'filthy toilets', 'unclean rooms'],
        'negation_hooks': ['unclean', 'unhygienic'],
    },
    'wait_time': {
        'keywords': {
            'wait', 'waiting', 'queue', 'line', 'delay', 'delays', 'appointment', 'appointments', 'schedule', 'scheduled',
            'hours', 'hour', 'minutes', 'time', 'hold', 'hold-up', 'backlog', 'crowded', 'rush', 'token'
        },
        'positive_terms': {'short', 'quick', 'fast', 'efficient', 'prompt', 'timely', 'smooth', 'minimal', 'instant', 'swift'},
        'negative_terms': {'long', 'slow', 'endless', 'forever', 'delayed', 'late', 'ridiculous', 'awful', 'terrible', 'crowded', 'waiting', 'wait', 'waited', 'delay', 'idle', 'stuck', 'time'},
        'positive_phrases': ['hardly any wait', 'no waiting', 'super quick', 'fast appointment'],
        'negative_phrases': ['waited for hours', 'long waiting time', 'took forever', 'kept waiting', 'delay in appointment', 'wait for some time', 'had to wait', 'wait for time'],
        'negation_hooks': ['rescheduled', 'postponed'],
    },
    'treatment': {
        'keywords': {
            'treatment', 'treatments', 'therapy', 'therapies', 'procedure', 'procedures', 'surgery', 'surgeries', 'operation',
            'operations', 'care', 'care-plan', 'careplan', 'diagnosis', 'diagnosed', 'recovery', 'medication', 'medications',
            'healing', 'consultation', 'doctor', 'doctors', 'nurse', 'nurses', 'nursing', 'specialist', 'surgeon', 'physician',
            'consultant', 'followup', 'follow-up', 'treated'
        },
        'positive_terms': {'effective', 'successful', 'smooth', 'painless', 'thorough', 'gentle', 'life-saving', 'careful', 'precise', 'well-planned', 'quick', 'cured', 'recovered', 'improved', 'accurate', 'confidence', 'treated', 'better', 'fixed', 'resolved', 'ok', 'okay', 'fine', 'alright'},
        'negative_terms': {'ineffective', 'painful', 'botched', 'failed', 'rough', 'aggressive', 'harmful', 'rushed', 'incorrect', 'delayed', 'complicated', 'worse', 'suffered', 'mistake', 'negligent'},
        'positive_phrases': ['took great care', 'treatment was successful', 'quick recovery', 'saved my life'],
        'negative_phrases': ['wrong diagnosis', 'misdiagnosed', 'treatment failed', 'no improvement', 'unnecessary tests', 'did not like the doctor', 'didnt like the doctor', 'did not help', "didn't help", "didn't help me", 'procedure did not help', "procedure didn't help", 'did not work', "didn't work"],
        'negation_hooks': ['misdiagnosed', 'untrained'],
    },
}

ASPECT_LABELS = {
    'staff': 'Staff',
    'cleanliness': 'Cleanliness',
    'wait_time': 'Wait Time',
    'treatment': 'Treatment',
}

DEFICIT_TERMS = {'lack', 'lacking', 'shortage', 'shortages', 'scarce', 'scarcity', 'missing', 'absence', 'absent'}

CONTRACTIONS = {
    "isn't": "is not",
    "aren't": "are not",
    "can't": "cannot",
    "couldn't": "could not",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "hadn't": "had not",
    "hasn't": "has not",
    "haven't": "have not",
    "he's": "he is",
    "i'd": "i would",
    "i'll": "i will",
    "i'm": "i am",
    "i've": "i have",
    "it's": "it is",
    "let's": "let us",
    "she's": "she is",
    "shouldn't": "should not",
    "that's": "that is",
    "there's": "there is",
    "they're": "they are",
    "we're": "we are",
    "weren't": "were not",
    "what's": "what is",
    "who's": "who is",
    "won't": "will not",
    "wouldn't": "would not",
    "you're": "you are",
    "wasn't": "was not"
}


def _expand_contractions(text: str) -> str:
    pattern = re.compile('(' + '|'.join(map(re.escape, CONTRACTIONS.keys())) + ')', flags=re.IGNORECASE)
    return pattern.sub(lambda m: CONTRACTIONS.get(m.group(0).lower(), m.group(0)), text)


def _basic_clean(text: str) -> str:
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    text = re.sub(r'[^A-Za-z0-9\s!?]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _convert_emojis_to_text(text: str) -> str:
    if not text:
        return ''
    demojized = emoji.demojize(text, language='en')
    demojized = re.sub(r':([a-z0-9_+\-]+):', lambda m: ' ' + m.group(1).replace('_', ' ') + ' ', demojized)
    return demojized


def _tokenize_for_aspects(text: str):
    return re.findall(r"[a-z0-9']+", text.lower())


def _split_sentences(text: str):
    if not text:
        return []
    return [s.strip() for s in re.split(r'[.!?\n]+', text) if s.strip()]


def _sentence_mentions_aspect(tokens, keywords):
    return any(token in keywords for token in tokens)


def _count_phrase_hits(sentence_lower, phrases):
    if not phrases:
        return 0
    return sum(1 for phrase in phrases if phrase in sentence_lower)


def _has_deficit_near_keyword(tokens, keywords, positive_terms):
    for idx, token in enumerate(tokens):
        if token not in keywords:
            continue
        window = tokens[max(0, idx - 2): idx + 1]
        if any(t in positive_terms or t in POSITIVE_OUTCOME_TOKENS for t in window):
            continue
        if any(t in DEFICIT_TERMS for t in window):
            return True
    return False


def _score_sentence_for_aspect(tokens, sentence_lower, config):
    pos_terms = config.get('positive_terms', set())
    neg_terms = config.get('negative_terms', set())

    pos = _count_phrase_hits(sentence_lower, config.get('positive_phrases', [])) * 1.5
    neg = _count_phrase_hits(sentence_lower, config.get('negative_phrases', [])) * 1.5

    pos += sum(1 for token in tokens if token in pos_terms)
    neg += sum(1 for token in tokens if token in neg_terms)

    neg += _count_phrase_hits(sentence_lower, config.get('negation_hooks', [])) * 2

    if _has_deficit_near_keyword(tokens, config.get('keywords', set()), pos_terms):
        neg += 2

    # Contrast handling: if sentence has both positive and negative cues and a positive outcome, soften negatives
    if pos > 0 and neg > 0:
        if any(t in POSITIVE_OUTCOME_TOKENS for t in tokens) or ' but ' in sentence_lower or ' though ' in sentence_lower or ' however ' in sentence_lower or ' yet ' in sentence_lower:
            neg *= 0.6

    return pos, neg


def extract_aspects(text: str):
    sentences = _split_sentences(text)
    if not sentences:
        return []

    findings = []
    aspect_scores = {slug: {'pos': 0.0, 'neg': 0.0, 'hits': 0} for slug in ASPECT_PROFILES}

    for sentence in sentences:
        sentence_lower = sentence.lower()
        tokens = _tokenize_for_aspects(sentence)
        if not tokens:
            continue

        for slug, config in ASPECT_PROFILES.items():
            if not _sentence_mentions_aspect(tokens, config.get('keywords', set())):
                continue

            pos, neg = _score_sentence_for_aspect(tokens, sentence_lower, config)
            if pos == 0 and neg == 0:
                continue

            aspect_scores[slug]['pos'] += pos
            aspect_scores[slug]['neg'] += neg
            aspect_scores[slug]['hits'] += 1

    for slug, stats in aspect_scores.items():
        net = stats['pos'] - stats['neg']
        if stats['pos'] == stats['neg'] == 0:
            continue

        sentiment = 'positive' if net > 0 else 'negative'
        strength = round(abs(net) + (0.3 * stats['hits']), 2)

        if strength <= 0.5:
            continue

        findings.append({
            'aspect': ASPECT_LABELS.get(slug, slug.replace('_', ' ').title()),
            'sentiment': sentiment,
            'strength': strength,
        })

    findings.sort(key=lambda item: item.get('strength', 0), reverse=True)
    trimmed = [{'aspect': item['aspect'], 'sentiment': item['sentiment']} for item in findings[:4]]
    return trimmed


def _label_to_star(label: str) -> int:
    if not label:
        return 3
    lower = label.lower().strip()
    if 'very positive' in lower:
        return 5
    if 'positive' in lower and 'very' not in lower:
        return 4 if 'somewhat' in lower else 5
    if 'mixed' in lower or 'neutral' in lower:
        return 3
    if 'very negative' in lower:
        return 1
    if 'negative' in lower and 'very' not in lower:
        return 2
    if 'star' in lower:
        match = re.search(r'([1-5])', lower)
        if match:
            return int(match.group(1))
    if 'label' in lower:
        match = re.search(r'(\d+)', lower)
        if match:
            idx = int(match.group(1))
            return max(1, min(5, idx + 1))
    digits = re.findall(r'[1-5]', lower)
    if digits:
        return int(digits[0])
    return 3


def _run_star_models(text: str):
    results = []
    for name, model in star_rating_models.items():
        try:
            res = model(text[:512])[0]
            results.append({
                'model': name,
                'star': _label_to_star(res.get('label')),
                'score': float(res.get('score', 0) or 0),
            })
        except Exception:
            continue
    return results


def _aggregate_star_results(star_results):
    if not star_results:
        return 3, 0.5

    weighted = []
    for res in star_results:
        weight = res['score'] if res['score'] > 0 else 0.5
        weighted.append((res['star'], weight))

    total_weight = sum(w for _, w in weighted)
    if total_weight == 0:
        return 3, 0.5

    avg_star = sum(star * weight for star, weight in weighted) / total_weight
    confidence = min(1.0, max(0.0, total_weight / len(weighted)))
    return int(round(avg_star)), confidence


def preprocess_review(text: str) -> str:
    if not text:
        return ''

    with_emojis = _convert_emojis_to_text(text)
    cleaned = _expand_contractions(with_emojis)
    cleaned = _basic_clean(cleaned)
    cleaned = cleaned.lower()
    return cleaned.strip()


def _run_binary_models(text: str):
    results = []
    for name, model in binary_sentiment_models.items():
        try:
            res = model(text[:512])[0]
            label = res.get('label', '').lower()
            sentiment = 'positive' if label.startswith('pos') else 'negative'
            results.append({
                'model': name,
                'sentiment': sentiment,
                'score': float(res.get('score', 0) or 0),
            })
        except Exception:
            continue
    return results


def _aggregate_sentiment(star_rating, star_weight, binary_results):
    votes = []

    if star_rating is not None:
        star_sentiment = 'positive' if star_rating > 3 else 'negative'
        votes.append({'sentiment': star_sentiment, 'score': max(0.5, star_weight), 'source': 'star_rating'})

    for result in binary_results:
        votes.append({
            'sentiment': result['sentiment'],
            'score': result['score'],
            'source': result['model'],
        })

    if not votes:
        return 'positive', 0.5, votes

    positive = sum(v['score'] for v in votes if v['sentiment'] == 'positive')
    negative = sum(v['score'] for v in votes if v['sentiment'] == 'negative')

    if positive == negative:
        final_sentiment = votes[0]['sentiment']
        confidence = votes[0]['score']
    elif positive > negative:
        final_sentiment = 'positive'
        confidence = positive / (positive + negative)
    else:
        final_sentiment = 'negative'
        confidence = negative / (positive + negative)

    return final_sentiment, round(confidence, 2), votes


def analyze_review(text: str):
    raw_text = text or ''
    cleaned_text = preprocess_review(raw_text)
    text_for_models = cleaned_text or raw_text

    star_results = _run_star_models(text_for_models)
    star_rating, star_weight = _aggregate_star_results(star_results)

    binary_results = _run_binary_models(text_for_models)
    sentiment_label, confidence, _votes = _aggregate_sentiment(star_rating, star_weight, binary_results)

    aspects = extract_aspects(raw_text)

    strong_failure = re.search(r"(didn't help|did not help|didn't work|did not work|no improvement|procedure (didn't|did not) help|treatment failed)", raw_text, flags=re.IGNORECASE)
    has_positive_outcome = any(tok in cleaned_text.split() for tok in POSITIVE_OUTCOME_TOKENS)

    if strong_failure and sentiment_label == 'positive' and not has_positive_outcome:
        sentiment_label = 'negative'
        confidence = max(confidence, 0.55)

    if sentiment_label == 'negative' and has_positive_outcome and not strong_failure:
        # If treatment succeeded or outcome words exist without strong failure, lean positive to avoid over-weighting minor negatives
        sentiment_label = 'positive'
        confidence = max(confidence, 0.55)

    return {
        'sentiment': sentiment_label,
        'score': round(confidence, 2),
        'star_rating': star_rating,
        'aspects': aspects,
    }
