from pathlib import Path
from pprint import pprint

import requests
from psychology_rules import psychology_risk_scores
from transformers import pipeline

LOW_RISK_THRESHOLD = 0.0
HIGH_RISK_THRESHOLD = 0.6
ACTIVE_FACTOR_THRESHOLD = 0.25

MODEL_DIR = Path("spam_model")
MODEL_FILE = MODEL_DIR / "model.safetensors"
MODEL_WEIGHTS_URL = "https://huggingface.co/bahaasobeh/blinkguard/resolve/main/model.safetensors"


def ensure_model_weights():
    if MODEL_FILE.exists():
        return

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading model weights from {MODEL_WEIGHTS_URL}...")
    response = requests.get(MODEL_WEIGHTS_URL, stream=True)
    response.raise_for_status()

    with open(MODEL_FILE, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print(f"Saved model weights to {MODEL_FILE}")


ensure_model_weights()

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

spam_detector = pipeline(
    "text-classification",
    model=str(MODEL_DIR),
    tokenizer=str(MODEL_DIR),
)


def ml_risk_score(ml_result):
    if ml_result["label"] == "LABEL_1":
        return ml_result["score"]
    return 1 - ml_result["score"]


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
    if score > LOW_RISK_THRESHOLD:
        return "medium"
    return "low"


def final_decision(score):
    if score >= HIGH_RISK_THRESHOLD:
        return "phishing"
    if score > LOW_RISK_THRESHOLD:
        return "suspicious"
    return "not phishing"


def analyze_message(message: str):
    ml_result = spam_detector(message)[0]
    ml_prediction = "spam" if ml_result["label"] == "LABEL_1" else "not spam"
    ml_confidence = round(ml_result["score"], 2)

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
        "final_decision": final_decision(final_risk),
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
