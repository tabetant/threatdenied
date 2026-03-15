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

    ai_verdict = ai_result.get("verdict", "suspicious")
    ai_summary = ai_result.get("summary", "")

    # ── CONSISTENCY SAFEGUARD ──────────────────────────────────────────────────
    # If the scorer's classification matches the AI's verdict, use the AI summary
    # directly. If they disagree, build a new summary from the signals so the
    # explanation never contradicts the displayed verdict.
    if _verdicts_agree(classification, ai_verdict) and ai_summary:
        summary = ai_summary
    else:
        summary = _build_summary(classification, confidence, fraud_score, signals, sc, ua, ca)

    return {
        "classification": classification,
        "fraud_score": round(fraud_score, 1),
        "confidence": round(confidence, 1),
        "signals_triggered": signals,
        "summary": summary
    }


def _verdicts_agree(scorer_verdict: str, ai_verdict: str) -> bool:
    """Check if the scorer and AI agree on the verdict direction."""
    if not ai_verdict:
        return False
    s = scorer_verdict.lower()
    a = ai_verdict.lower()
    # Exact match
    if s == a:
        return True
    # Both on the same side of the line (suspicious is closer to fraud than legitimate)
    if s in ("fraud", "suspicious") and a in ("fraud", "suspicious"):
        return True
    return False


def _build_summary(classification: str, confidence: float, fraud_score: float,
                   signals: list, sc: dict, ua: dict, ca: dict) -> str:
    """Build a verdict-consistent summary from the triggered signals."""

    fraud_signals = [s for s in signals if s["pts"] > 0]
    legit_signals = [s for s in signals if s["pts"] < 0]

    if classification == "fraud":
        parts = []
        sender_addr = sc.get("sender_address", "the sender")
        if any(s["id"] in ("S1", "S2", "S3") for s in fraud_signals):
            if sc.get("is_lookalike_domain"):
                real = sc.get("lookalike_of", "a legitimate TD domain")
                parts.append(f"The sender address {sender_addr} uses a lookalike domain designed to impersonate {real}")
            else:
                parts.append(f"The sender {sender_addr} is not a recognized TD Bank address")

        url_flags = [s for s in fraud_signals if s["id"] in ("S5", "S6", "S7", "S9")]
        if url_flags:
            risky = ua.get("high_risk_urls", ua.get("lookalike_url_details", []))
            if risky:
                parts.append(f"embedded links point to suspicious domains ({', '.join(risky[:2])})")
            else:
                parts.append("embedded links raise significant risk — lookalike or newly registered domains detected")

        content_flags = [s for s in fraud_signals if s["id"] in ("S10", "S11", "S14", "S15", "S16")]
        if content_flags:
            tactics = []
            if any(s["id"] == "S10" for s in content_flags):
                tactics.append("urgency pressure")
            if any(s["id"] == "S11" for s in content_flags):
                info = ca.get("personal_info_requested", [])
                tactics.append(f"requests for sensitive information ({', '.join(info[:3])})" if info else "requests for sensitive information")
            if any(s["id"] == "S14" for s in content_flags):
                tactics.append("threatening language")
            if any(s["id"] == "S16" for s in content_flags):
                tactics.append("emotional manipulation")
            if any(s["id"] == "S15" for s in content_flags):
                tactics.append("a suspicious call to action")
            if tactics:
                parts.append(f"the message employs {', '.join(tactics)}")

        if not parts:
            parts.append("multiple fraud indicators were detected across sender, content, and link analysis")

        # Join naturally
        if len(parts) == 1:
            body = parts[0]
        elif len(parts) == 2:
            body = f"{parts[0]}, and {parts[1]}"
        else:
            body = f"{parts[0]}. Additionally, {parts[1]}, and {parts[2]}"

        return f"{body}. This message shows clear characteristics of a phishing attempt and should not be trusted."

    elif classification == "legitimate":
        parts = []
        sender_addr = sc.get("sender_address", "the sender")
        if any(s["id"] == "L1" for s in legit_signals):
            parts.append(f"The sender {sender_addr} is a verified TD Bank address")

        if any(s["id"] == "L3" for s in legit_signals):
            parts.append("the message closely matches TD's standard communication templates")
        if any(s["id"] == "L4" for s in legit_signals):
            parts.append("the tone is professional with no urgency pressure")
        if any(s["id"] == "L2" for s in legit_signals):
            parts.append("all embedded links resolve to legitimate TD domains")

        if not parts:
            parts.append("No significant fraud indicators were detected in this message")

        if len(parts) == 1:
            body = parts[0]
        elif len(parts) == 2:
            body = f"{parts[0]}, and {parts[1]}"
        else:
            body = f"{parts[0]}, {parts[1]}, and {parts[2]}"

        return f"{body}. This communication appears consistent with authentic TD Bank correspondence."

    else:
        # Suspicious
        fraud_names = [s["name"] for s in fraud_signals[:3]]
        legit_names = [s["name"] for s in legit_signals[:2]]
        parts = []
        if fraud_names:
            parts.append(f"risk signals include {', '.join(fraud_names)}")
        if legit_names:
            parts.append(f"however {'and '.join(legit_names).lower()} provide some reassurance")

        body = "; ".join(parts) if parts else "The analysis produced mixed signals"
        return f"This message warrants caution — {body}. A TD analyst will review this submission and follow up with a definitive verdict."
