def compute_verdict(ai_result: dict) -> dict:
    fraud_score = 0.0
    signals = []

    sc = ai_result.get("sender_check", {})
    ua = ai_result.get("url_analysis", {})
    ca = ai_result.get("content_analysis", {})

    # ── SENDER SIGNALS (max 25) ───────────────────────────────────────────────
    if sc.get("is_known_td_sender") is False:
        fraud_score += 12
        signals.append({"id": "S1", "name": "Unknown sender", "pts": 12})
    if sc.get("is_lookalike_domain") is True:
        fraud_score += 10
        signals.append({"id": "S2", "name": "Lookalike domain", "pts": 10, "detail": sc.get("lookalike_of")})
    if sc.get("display_name_mismatch") is True:
        fraud_score += 5
        signals.append({"id": "S3", "name": "Display name mismatch", "pts": 5})
    if "fail" in (sc.get("spf_dkim_status") or "").lower():
        fraud_score += 8
        signals.append({"id": "S4", "name": "SPF/DKIM failure", "pts": 8})

    # ── URL SIGNALS (max 30) ──────────────────────────────────────────────────
    if ua.get("has_lookalike_urls") is True:
        fraud_score += 12
        signals.append({"id": "S5", "name": "Lookalike URL", "pts": 12})
    if ua.get("has_new_domains") is True:
        fraud_score += 8
        signals.append({"id": "S6", "name": "New domain", "pts": 8})
    if ua.get("has_url_shorteners") is True:
        fraud_score += 5
        signals.append({"id": "S7", "name": "URL shortener", "pts": 5})
    if ua.get("has_http_only") is True:
        fraud_score += 3
        signals.append({"id": "S8", "name": "No HTTPS", "pts": 3})
    if len(ua.get("high_risk_urls", [])) > 0:
        fraud_score += 7
        signals.append({"id": "S9", "name": "High-risk URL", "pts": 7})

    # ── CONTENT SIGNALS (max 35) ──────────────────────────────────────────────
    urgency = ca.get("urgency_score", 0)
    if urgency >= 7:
        fraud_score += 8
        signals.append({"id": "S10", "name": "High urgency", "pts": 8})
    elif urgency >= 4:
        fraud_score += 4
        signals.append({"id": "S10", "name": "Moderate urgency", "pts": 4})

    if len(ca.get("personal_info_requested", [])) > 0:
        fraud_score += 10
        signals.append({"id": "S11", "name": "Requests personal info", "pts": 10, "detail": ", ".join(ca["personal_info_requested"])})

    grammar = (ca.get("grammar_quality") or "").lower()
    if grammar in ["poor", "very_poor"]:
        fraud_score += 5
        signals.append({"id": "S12", "name": "Poor grammar", "pts": 5})

    template_sim = ca.get("template_similarity", 50)
    if template_sim < 30:
        fraud_score += 7
        signals.append({"id": "S13", "name": "Template mismatch", "pts": 7})
    elif template_sim < 50:
        fraud_score += 3
        signals.append({"id": "S13", "name": "Low template match", "pts": 3})

    threat = (ca.get("threat_level") or "").lower()
    if threat in ["moderate", "severe"]:
        fraud_score += 5
        signals.append({"id": "S14", "name": "Threat language", "pts": 5})

    if ca.get("call_to_action_legitimate") is False:
        fraud_score += 6
        signals.append({"id": "S15", "name": "Suspicious CTA", "pts": 6})

    if len(ca.get("emotional_manipulation", [])) >= 2:
        fraud_score += 4
        signals.append({"id": "S16", "name": "Emotional manipulation", "pts": 4})

    # ── LEGITIMACY SIGNALS (reduce score) ─────────────────────────────────────
    if sc.get("is_known_td_sender") is True:
        fraud_score -= 15
        signals.append({"id": "L1", "name": "Known TD sender", "pts": -15})

    all_urls = ua.get("urls_found", [])
    if all_urls and not ua.get("has_lookalike_urls") and not ua.get("has_new_domains") and not ua.get("high_risk_urls"):
        fraud_score -= 10
        signals.append({"id": "L2", "name": "All URLs legit", "pts": -10})

    if template_sim >= 80:
        fraud_score -= 8
        signals.append({"id": "L3", "name": "High template match", "pts": -8})

    if grammar == "professional" and urgency <= 2:
        fraud_score -= 5
        signals.append({"id": "L4", "name": "Professional tone", "pts": -5})

    # ── Clamp and classify ─────────────────────────────────────────────────────
    fraud_score = max(0.0, min(100.0, fraud_score))

    if fraud_score >= 56:
        classification = "fraud"
        confidence = fraud_score
    elif fraud_score >= 26:
        classification = "suspicious"
        confidence = 50
    else:
        classification = "legitimate"
        confidence = 100 - fraud_score

    return {
        "classification": classification,
        "fraud_score": round(fraud_score, 1),
        "confidence": round(confidence, 1),
        "signals_triggered": signals,
        "summary": ai_result.get("summary", "")
    }
