"""
Verdict aggregator — combines all check scores into a final fraud/legitimate/inconclusive verdict.
"""

# Weight of each check in final confidence score
WEIGHTS = {
    "sender":      0.20,
    "url":         0.30,
    "content_ai":  0.35,
    "template":    0.10,
    "campaign":    0.05,
}

STATUS_SCORE = {
    "pass":    1.0,
    "fail":    0.0,
    "warning": 0.4,
    "info":    0.5,
}


def aggregate(checks: list[dict]) -> dict:
    """
    checks: list of ForensicCheckEvent dicts (excluding verdict)
    Returns: {verdict: str, confidence: float}
    """
    weighted_sum = 0.0
    total_weight = 0.0

    for check in checks:
        check_name = check.get("check")
        if check_name not in WEIGHTS:
            continue

        weight = WEIGHTS[check_name]
        # Prefer explicit score, fall back to status mapping
        score = check.get("score")
        if score is None:
            score = STATUS_SCORE.get(check.get("status", "info"), 0.5)

        weighted_sum += score * weight
        total_weight += weight

    if total_weight == 0:
        return {"verdict": "inconclusive", "confidence": 0.0}

    legit_confidence = weighted_sum / total_weight

    if legit_confidence < 0.25:
        return {"verdict": "fraud", "confidence": round(1 - legit_confidence, 3)}
    elif legit_confidence > 0.70:
        return {"verdict": "legitimate", "confidence": round(legit_confidence, 3)}
    else:
        return {"verdict": "inconclusive", "confidence": round(max(legit_confidence, 1 - legit_confidence), 3)}
