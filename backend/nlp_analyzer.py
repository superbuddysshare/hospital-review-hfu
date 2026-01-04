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

# DeBERTa MNLI for aspects (requires protobuf and sentencepiece installed)
aspect_classifier = pipeline(
    "zero-shot-classification",
    model="MoritzLaurer/DeBERTa-v3-base-mnli",
    device=DEVICE,
)

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


ASPECT_LABELS = {
    'staff': 'Staff',
    'wait_time': 'Wait Time',
    'treatment': 'Treatment',
    'insurance': 'Insurance',
}

_WAIT_TIME_ALIASES = [
    'Wait Time',
    'Waiting Time',
    'Long Wait',
    'Long Waiting Time',
    'Wait Times',
    'Queue Time',
    'Delays',
]

_CANONICAL_ASPECT_MAP = {value.lower(): value for value in ASPECT_LABELS.values()}
for alias in _WAIT_TIME_ALIASES:
    _CANONICAL_ASPECT_MAP[alias.lower()] = ASPECT_LABELS['wait_time']

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




def _canonicalize_aspect(label: str) -> str:
    if not label:
        return ''
    return _CANONICAL_ASPECT_MAP.get(label.strip().lower(), '')


def _model_aspect_analysis(text: str):
    if not text or not text.strip():
        return []

    candidate_labels = []
    seen = set()

    def _add_candidate(label: str):
        if label in seen:
            return
        seen.add(label)
        candidate_labels.append(f"{label} positive")
        candidate_labels.append(f"{label} negative")

    for label in ASPECT_LABELS.values():
        _add_candidate(label)
    for alias in _WAIT_TIME_ALIASES:
        _add_candidate(alias)

    try:
        result = aspect_classifier(text, candidate_labels=candidate_labels, multi_label=True)
    except Exception:
        return []

    scores = {}
    for lbl, score in zip(result.get('labels', []), result.get('scores', [])):
        parts = lbl.split(' ', 1)
        if len(parts) != 2:
            continue
        aspect_label, sentiment = parts
        canonical = _canonicalize_aspect(aspect_label)
        if not canonical:
            continue
        scores.setdefault(canonical, {})[sentiment] = score

    findings = []
    for aspect_label, sent_dict in scores.items():
        pos_score = sent_dict.get('positive', 0)
        neg_score = sent_dict.get('negative', 0)
        if max(pos_score, neg_score) < 0.3:
            continue
        sentiment = 'positive' if pos_score >= neg_score else 'negative'
        strength = round(abs(pos_score - neg_score), 2)
        findings.append({'aspect': aspect_label, 'sentiment': sentiment, 'strength': strength})

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


VALID_MODES = {'combined', 'binary', 'star'}
_ACTIVE_MODE = 'combined'


def set_analysis_mode(mode: str) -> str:
    """Set global analysis mode for subsequent calls."""
    global _ACTIVE_MODE
    normalized = (mode or 'combined').lower()
    if normalized not in VALID_MODES:
        normalized = 'combined'
    _ACTIVE_MODE = normalized
    return _ACTIVE_MODE


def get_analysis_mode() -> str:
    return _ACTIVE_MODE


def analyze_review(text: str):
    raw_text = text or ''
    cleaned_text = preprocess_review(raw_text)
    text_for_models = cleaned_text or raw_text

    normalized_mode = _ACTIVE_MODE

    run_star = normalized_mode in {'combined', 'star'}
    run_binary = normalized_mode in {'combined', 'binary'}

    star_results = []
    star_rating = None
    star_weight = 0.0
    if run_star:
        star_results = _run_star_models(text_for_models)
        star_rating, star_weight = _aggregate_star_results(star_results)

    binary_results = _run_binary_models(text_for_models) if run_binary else []

    sentiment_label, confidence, _votes = _aggregate_sentiment(star_rating, star_weight, binary_results)

    aspects = _model_aspect_analysis(raw_text)

    strong_failure = re.search(r"(didn't help|did not help|didn't work|did not work|no improvement|procedure (didn't|did not) help|treatment failed)", raw_text, flags=re.IGNORECASE)
    has_positive_outcome = any(tok in cleaned_text.split() for tok in POSITIVE_OUTCOME_TOKENS)

    if strong_failure and sentiment_label == 'positive' and not has_positive_outcome:
        sentiment_label = 'negative'
        confidence = max(confidence, 0.55)


    return {
        'sentiment': sentiment_label,
        'score': round(confidence, 2),
        'star_rating': star_rating,
        'aspects': aspects,
    }
