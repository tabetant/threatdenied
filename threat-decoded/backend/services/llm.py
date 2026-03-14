import anthropic
import json
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def call_claude(system_prompt: str, user_message: str, model: str = "claude-sonnet-4-20250514") -> dict:
    """
    Makes a single Claude API call. Returns parsed JSON.
    Falls back to returning raw text wrapped in a dict if JSON parsing fails.
    """
    response = client.messages.create(
        model=model,
        max_tokens=2000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )

    raw_text = response.content[0].text

    try:
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return json.loads(cleaned.strip())
    except json.JSONDecodeError:
        return {"raw_response": raw_text, "parse_error": True}


async def run_full_analysis(content: str, content_type: str, known_senders: dict, td_templates: dict, existing_campaigns: list) -> dict:
    """
    Runs all 4 analysis steps sequentially.
    Each step receives the content + results of all previous steps.
    Returns a dict with all 4 step results + a final aggregated verdict.
    """
    results = {}

    from prompts.step1_header import get_step1_prompt
    step1_system, step1_user = get_step1_prompt(content, content_type, known_senders)
    results["step1_header"] = call_claude(step1_system, step1_user)

    from prompts.step2_links import get_step2_prompt
    step2_system, step2_user = get_step2_prompt(content, content_type, known_senders, results["step1_header"])
    results["step2_links"] = call_claude(step2_system, step2_user)

    from prompts.step3_body import get_step3_prompt
    step3_system, step3_user = get_step3_prompt(content, content_type, td_templates, results["step1_header"], results["step2_links"])
    results["step3_body"] = call_claude(step3_system, step3_user)

    from prompts.step4_campaign import get_step4_prompt
    step4_system, step4_user = get_step4_prompt(content, content_type, existing_campaigns, results["step1_header"], results["step2_links"], results["step3_body"])
    results["step4_campaign"] = call_claude(step4_system, step4_user)

    results["final_verdict"] = compute_weighted_verdict(results)

    return results


def compute_weighted_verdict(results: dict) -> dict:
    """
    Deterministic weighted scoring. Each signal from the 4 steps contributes
    a specific number of points to a fraud score (0–100).
    """
    fraud_score = 0.0
    signals_triggered = []

    step1 = results.get("step1_header", {})
    step2 = results.get("step2_links", {})
    step3 = results.get("step3_body", {})
    step4 = results.get("step4_campaign", {})

    # ── STEP 1: Header / Sender (max 25 pts) ──────────────────────────────────

    if step1.get("is_known_td_sender") is False:
        fraud_score += 12
        signals_triggered.append({"signal": "S1_UNKNOWN_SENDER", "points": 12, "detail": f"Sender '{step1.get('sender_identified', '?')}' is not in TD's known sender list"})

    if step1.get("is_lookalike_domain") is True:
        fraud_score += 10
        signals_triggered.append({"signal": "S2_LOOKALIKE_DOMAIN", "points": 10, "detail": f"Domain impersonates '{step1.get('lookalike_of', 'td.com')}'"})

    sender_id = (step1.get("sender_identified") or "").lower()
    display_name = (step1.get("sender_display_name") or "").lower()
    if display_name and "td" in display_name and sender_id and not any(d in sender_id for d in ["td.com", "tdbank.com", "td.ca"]):
        fraud_score += 5
        signals_triggered.append({"signal": "S3_DISPLAY_NAME_MISMATCH", "points": 5, "detail": f"Display name '{step1.get('sender_display_name')}' doesn't match sender address"})

    auth_result = (step1.get("spf_dkim_dmarc") or "").lower()
    if "fail" in auth_result:
        fraud_score += 8
        signals_triggered.append({"signal": "S4_AUTH_FAILURE", "points": 8, "detail": f"Email authentication failed: {step1.get('spf_dkim_dmarc')}"})

    # ── STEP 2: Links / URLs (max 30 pts) ─────────────────────────────────────

    url_analyses = step2.get("analysis", [])

    lookalike_urls = [u for u in url_analyses if u.get("is_lookalike")]
    if lookalike_urls:
        fraud_score += 12
        signals_triggered.append({"signal": "S5_LOOKALIKE_URL", "points": 12, "detail": f"URL(s) use lookalike domain: {[u.get('url') for u in lookalike_urls]}"})

    new_domains = [u for u in url_analyses if "new" in (u.get("estimated_domain_age") or "").lower()]
    if new_domains:
        fraud_score += 8
        signals_triggered.append({"signal": "S6_NEW_DOMAIN", "points": 8, "detail": "URL domain(s) appear newly registered"})

    shorteners = [u for u in url_analyses if u.get("uses_shortener")]
    if shorteners:
        fraud_score += 5
        signals_triggered.append({"signal": "S7_URL_SHORTENER", "points": 5, "detail": "URL shortener(s) hiding real destination"})

    no_https = [u for u in url_analyses if u.get("uses_https") is False]
    if no_https:
        fraud_score += 3
        signals_triggered.append({"signal": "S8_NO_HTTPS", "points": 3, "detail": "URL(s) using insecure HTTP"})

    high_risk = [u for u in url_analyses if u.get("risk_level") == "high"]
    if high_risk:
        fraud_score += 7
        signals_triggered.append({"signal": "S9_HIGH_RISK_URL", "points": 7, "detail": f"{len(high_risk)} URL(s) rated high risk"})

    # ── STEP 3: Body Content (max 35 pts) ─────────────────────────────────────

    urgency = step3.get("urgency_score", 0)
    if urgency >= 7:
        fraud_score += 8
        signals_triggered.append({"signal": "S10_HIGH_URGENCY", "points": 8, "detail": f"Urgency score {urgency}/10 — heavy pressure tactics"})
    elif urgency >= 4:
        fraud_score += 4
        signals_triggered.append({"signal": "S10_MODERATE_URGENCY", "points": 4, "detail": f"Urgency score {urgency}/10 — moderate pressure"})

    personal_info = step3.get("personal_info_requested", [])
    if personal_info:
        fraud_score += 10
        signals_triggered.append({"signal": "S11_PERSONAL_INFO_REQUEST", "points": 10, "detail": f"Asks for: {', '.join(personal_info)}"})

    grammar = (step3.get("grammar_quality") or "").lower()
    if grammar in ["poor", "very_poor"]:
        fraud_score += 5
        signals_triggered.append({"signal": "S12_POOR_GRAMMAR", "points": 5, "detail": f"Grammar quality: {grammar}"})

    template_sim = step3.get("template_match", {}).get("similarity_score", 50)
    if template_sim < 30:
        fraud_score += 7
        signals_triggered.append({"signal": "S13_TEMPLATE_MISMATCH", "points": 7, "detail": f"Only {template_sim}% match to real TD communications"})
    elif template_sim < 50:
        fraud_score += 3
        signals_triggered.append({"signal": "S13_TEMPLATE_LOW_MATCH", "points": 3, "detail": f"{template_sim}% match to real TD communications"})

    threat_level = (step3.get("threat_level") or "").lower()
    if threat_level in ["moderate", "severe"]:
        fraud_score += 5
        signals_triggered.append({"signal": "S14_THREAT_LANGUAGE", "points": 5, "detail": f"Threat level: {threat_level}"})

    if step3.get("call_to_action_legitimate") is False:
        fraud_score += 6
        signals_triggered.append({"signal": "S15_BAD_CTA", "points": 6, "detail": f"Suspicious call to action: {step3.get('call_to_action', '?')}"})

    emo_tactics = step3.get("emotional_manipulation_tactics", [])
    if len(emo_tactics) >= 2:
        fraud_score += 4
        signals_triggered.append({"signal": "S16_EMOTIONAL_MANIPULATION", "points": 4, "detail": f"Tactics: {', '.join(emo_tactics[:3])}"})

    # ── STEP 4: Campaign Match (max 10 pts) ───────────────────────────────────

    if step4.get("matches_existing_campaign") is True and step4.get("match_confidence", 0) > 60:
        fraud_score += 10
        signals_triggered.append({"signal": "S17_CAMPAIGN_MATCH", "points": 10, "detail": f"Matches campaign '{step4.get('matched_campaign_name')}' (confidence: {step4.get('match_confidence')}%)"})
    elif step4.get("is_new_campaign") is True:
        fraud_score += 6
        signals_triggered.append({"signal": "S18_NEW_CAMPAIGN", "points": 6, "detail": f"New campaign pattern: {step4.get('suggested_campaign_name', 'unnamed')}"})

    # ── Legitimacy signals (subtract) ─────────────────────────────────────────

    if step1.get("is_known_td_sender") is True:
        fraud_score -= 15
        signals_triggered.append({"signal": "L1_KNOWN_SENDER", "points": -15, "detail": "Sender is in TD's verified sender list"})

    if url_analyses and all(u.get("is_known_td_domain") for u in url_analyses):
        fraud_score -= 10
        signals_triggered.append({"signal": "L2_ALL_URLS_LEGIT", "points": -10, "detail": "All URLs point to verified TD domains"})

    if template_sim >= 80:
        fraud_score -= 8
        signals_triggered.append({"signal": "L4_HIGH_TEMPLATE_MATCH", "points": -8, "detail": f"{template_sim}% match to real TD communications"})

    if grammar == "professional" and urgency <= 2:
        fraud_score -= 5
        signals_triggered.append({"signal": "L5_CLEAN_CONTENT", "points": -5, "detail": "Professional grammar with no urgency tactics"})

    # ── Clamp and classify ────────────────────────────────────────────────────

    fraud_score = max(0.0, min(100.0, fraud_score))

    if fraud_score >= 56:
        classification = "fraud"
    elif fraud_score >= 26:
        classification = "suspicious"
    else:
        classification = "legitimate"

    return {
        "classification": classification,
        "fraud_score": round(fraud_score, 1),
        "confidence": round(fraud_score if classification == "fraud" else (100 - fraud_score), 1),
        "signals_triggered": signals_triggered,
        "signals_count": len(signals_triggered),
        "step_verdicts": {
            "header": step1.get("verdict", "unknown"),
            "links": step2.get("verdict", "unknown"),
            "body": step3.get("verdict", "unknown"),
            "campaign": step4.get("verdict", "unknown"),
        },
        "score_breakdown": {
            "header_signals": sum(s["points"] for s in signals_triggered if s["signal"][0] in ("S", "L") and s["signal"].split("_")[0] in ("S1", "S2", "S3", "S4", "L1")),
            "link_signals": sum(s["points"] for s in signals_triggered if s["signal"].split("_")[0] in ("S5", "S6", "S7", "S8", "S9", "L2")),
            "body_signals": sum(s["points"] for s in signals_triggered if s["signal"].split("_")[0] in ("S10", "S11", "S12", "S13", "S14", "S15", "S16", "L4", "L5")),
            "campaign_signals": sum(s["points"] for s in signals_triggered if s["signal"].split("_")[0] in ("S17", "S18")),
        }
    }
