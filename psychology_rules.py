import re

PSYCHOLOGY_RULES = {
    "urgency": [
        "urgent",
        "immediately",
        "now",
        "act fast",
        "within",
        "today",
        "asap",
    ],
    "authority": [
        "bank",
        "paypal",
        "security team",
        "administrator",
        "official",
        "account suspended",
        "account limited",
        "verification required",
    ],
    "fear": [
        "suspended",
        "blocked",
        "compromised",
        "unauthorized",
        "risk",
        "fraud",
        "security alert",
    ],
    "reward": [
        "free",
        "win",
        "winner",
        "prize",
        "gift",
        "reward",
        "bonus",
        "cash",
    ],
    "scarcity": [
        "limited",
        "last chance",
        "only today",
        "expires",
        "final notice",
    ],
    "curiosity": [
        "click here",
        "open",
        "view",
        "see details",
        "is this you",
    ],
}

PATTERN_RULES = {
    "link": [
        {"pattern": r"https?://", "ignore_case": True},
        {"pattern": r"www\.", "ignore_case": True},
        {"pattern": r"\bbit\.ly\b", "ignore_case": True},
        {"pattern": r"\btinyurl\.com\b", "ignore_case": True},
    ],
    "money": [
        {"pattern": r"\$\s?\d+(?:,\d{3})*(?:\.\d+)?", "ignore_case": False},
        {"pattern": r"\b\d+(?:,\d{3})?\s?(usd|dollars|eur|nis|dollar)\b", "ignore_case": True},
    ],
    "formatting": [
        {"pattern": r"!{2,}", "ignore_case": False},
        {"pattern": r"\?{2,}", "ignore_case": False},
        {"pattern": r"\b[A-Z]{4,}\b", "ignore_case": False},
    ],
    "contact_pressure": [
        {"pattern": r"\bverify\b", "ignore_case": True},
        {"pattern": r"\bconfirm\b", "ignore_case": True},
        {"pattern": r"\bupdate\b", "ignore_case": True},
        {"pattern": r"\breset\b", "ignore_case": True},
        {"pattern": r"\bclaim\b", "ignore_case": True},
    ],
}


def _keyword_hits(text: str, keywords: list[str]) -> int:
    hits = 0
    for keyword in keywords:
        pattern = r"\b{}\b".format(re.escape(keyword))
        if " " in keyword:
            if keyword in text:
                hits += 1
        elif re.search(pattern, text):
            hits += 1
    return hits


def _pattern_hits(text: str, rules: list[dict[str, object]]) -> int:
    hits = 0
    for rule in rules:
        flags = re.IGNORECASE if rule.get("ignore_case") else 0
        if re.search(rule["pattern"], text, flags):
            hits += 1
    return hits


def _normalized_score(hits: int, total_rules: int) -> float:
    if total_rules <= 0:
        return 0.0
    return round(min(hits / max(total_rules * 0.5, 1), 1.0), 2)


def psychology_risk_scores(text: str):
    text_l = text.lower()
    scores = {}

    for factor, keywords in PSYCHOLOGY_RULES.items():
        hits = _keyword_hits(text_l, keywords)
        scores[factor] = _normalized_score(hits, len(keywords))

    for factor, rules in PATTERN_RULES.items():
        hits = _pattern_hits(text, rules)
        scores[factor] = _normalized_score(hits, len(rules))

    return scores
