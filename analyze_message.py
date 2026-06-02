from pprint import pprint

from psychology_rules import psychology_risk_scores
from transformers import pipeline

LOW_RISK_THRESHOLD = 0.25
HIGH_RISK_THRESHOLD = 0.6
ACTIVE_FACTOR_THRESHOLD = 0.25

MODEL_REPO = "bahaasobeh/blinkguard"

MODEL_LABELS = {
    "label_0": "safe",
    "label_1": "spam",
    "label_2": "phishing",
}

PSYCHOLOGY_WEIGHTS = {
    "urgency": 1.1,
    "authority": 1.2,
    "fear": 1.0,
    "reward": 0.9,
    "scarcity": 0.8,
    "curiosity": 0.8,
    "link": 1.0,
    "money": 0.8,
    "formatting": 0.3,
    "contact_pressure": 1.2,
}

HIGH_SIGNAL_FACTORS = {
    "urgency",
    "authority",
    "fear",
    "contact_pressure",
    "link",
    "money",
    "curiosity",
    "reward",
    "scarcity",
}

spam_detector = None


def get_spam_detector():
    global spam_detector
    if spam_detector is None:
        spam_detector = pipeline(
            "text-classification",
            model=MODEL_REPO,
            tokenizer=MODEL_REPO,
        )
    return spam_detector


def _normalize_confidence(confidence):
    if isinstance(confidence, str):
        confidence = confidence.strip().rstrip("%")

    confidence = float(confidence)
    if confidence > 1:
        confidence = confidence / 100

    return max(0.0, min(confidence, 1.0))


def normalize_ml_result(ml_result):
    class_name = (
        ml_result.get("Class")
        or ml_result.get("class")
        or ml_result.get("label")
        or ""
    )
    confidence = (
        ml_result.get("Confidence")
        or ml_result.get("confidence")
        or ml_result.get("score")
        or 0.0
    )

    normalized_class = str(class_name).strip().lower()
    confidence = _normalize_confidence(confidence)

    normalized_class = MODEL_LABELS.get(normalized_class, normalized_class)

    if normalized_class in {"not spam", "ham"}:
        normalized_class = "safe"

    return {
        "class": normalized_class,
        "confidence": confidence,
        "raw": ml_result,
    }


def ml_risk_score(ml_result):
    ml_class = ml_result["class"]
    confidence = ml_result["confidence"]

    if ml_class == "phishing":
        return confidence
    if ml_class == "spam":
        return confidence
    if ml_class == "safe":
        return 1 - confidence

    return 0.5


def psychology_weighted_score(psychology_scores):
    weighted_sum = 0.0
    total_weight = 0.0

    for factor, score in psychology_scores.items():
        weight = PSYCHOLOGY_WEIGHTS.get(factor, 1.0)
        weighted_sum += score * weight
        total_weight += weight

    return round(weighted_sum / total_weight, 2) if total_weight else 0.0


def high_signal_count(psychology_scores):
    return sum(
        1
        for factor, score in psychology_scores.items()
        if factor in HIGH_SIGNAL_FACTORS and score >= ACTIVE_FACTOR_THRESHOLD
    )


def combined_risk_score(ml_result, psychology_scores):
    ml_risk = ml_risk_score(ml_result)
    psychology_score = psychology_weighted_score(psychology_scores)
    signal_count = high_signal_count(psychology_scores)

    final_score = (0.55 * ml_risk) + (0.45 * psychology_score)

    if ml_result["class"] == "phishing":
        final_score = max(final_score, ml_risk)

    if ml_risk < 0.2 and signal_count >= 3:
        final_score += 0.2

    if ml_risk < 0.2 and signal_count >= 4:
        final_score += 0.1

    if psychology_scores.get("authority", 0) >= 0.25 and psychology_scores.get("contact_pressure", 0) >= 0.25:
        final_score += 0.1

    if psychology_scores.get("urgency", 0) >= 0.25 and psychology_scores.get("fear", 0) >= 0.25:
        final_score += 0.1

    if psychology_scores.get("urgency", 0) >= 0.25 and psychology_scores.get("contact_pressure", 0) >= 0.25:
        final_score += 0.1

    if psychology_scores.get("link", 0) >= 0.25 and psychology_scores.get("contact_pressure", 0) >= 0.25:
        final_score += 0.1

    if psychology_scores.get("scarcity", 0) >= 0.25 and psychology_scores.get("contact_pressure", 0) >= 0.25:
        final_score += 0.1

    return round(min(final_score, 1.0), 2)


def risk_band(score):
    if score >= HIGH_RISK_THRESHOLD:
        return "high"
    if score >= LOW_RISK_THRESHOLD:
        return "medium"
    return "low"


def final_decision(score, ml_result):
    ml_class = ml_result["class"]
    confidence = ml_result["confidence"]

    if ml_class == "phishing":
        if confidence >= HIGH_RISK_THRESHOLD:
            return "phishing"
        return "suspicious"

    if ml_class == "spam":
        return "suspicious"

    if score >= HIGH_RISK_THRESHOLD:
        return "phishing"
    if score >= LOW_RISK_THRESHOLD:
        return "suspicious"
    return "not phishing"


def analyze_message(message: str):
    raw_ml_result = get_spam_detector()(message)[0]
    ml_result = normalize_ml_result(raw_ml_result)
    ml_prediction = ml_result["class"]
    ml_confidence = round(ml_result["confidence"], 2)

    psychology_scores = psychology_risk_scores(message)
    psychology_score = psychology_weighted_score(psychology_scores)
    active_psychology = [
        factor for factor, score in psychology_scores.items() if score >= ACTIVE_FACTOR_THRESHOLD
    ]

    final_risk = combined_risk_score(ml_result, psychology_scores)

    return {
        "message": message,
        "ml_prediction": ml_prediction,
        "ml_confidence": ml_confidence,
        "ml_risk_score": round(ml_risk_score(ml_result), 2),
        "final_decision": final_decision(final_risk, ml_result),
        "risk_band": risk_band(final_risk),
        "final_risk_score": final_risk,
        "psychology_average": psychology_score,
        "high_signal_count": high_signal_count(psychology_scores),
        "psychological_factors": active_psychology,
        "psychology_risk_scores": psychology_scores,
    }


if __name__ == "__main__":
    tests = [
        "URGENT: Your PayPal account has been suspended. Verify immediately.",
        "Congratulations! You won a $1000 gift card!",
        "Hey, are we still meeting tonight?",
        "Final notice: claim your reward now!",
        "hii this is bahaa call me once you get my message",
        "hii this is bahaa call me once you get my message click here to get 100 dollar",
        "Congratulations! You have won a $1,000 gift card.",
        "Please press here to update your data immediately.",
        "call me im bahaa sobeh",
    ]

    print("-" * 60)
    for msg in tests:
        pprint(analyze_message(msg))
        print("-" * 60)
