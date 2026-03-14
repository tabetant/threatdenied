"""
Claude-powered fraud content analysis.
Calls the fraud_analysis system prompt and returns both the raw AI result
and a ForensicCheckEvent dict ready for SSE streaming.
"""
import json
from ai.client import call_ai, load_prompt


def analyze_content(content: str, content_type: str) -> dict:
    """
    Send content to Claude for forensic fraud analysis.
    Returns the parsed JSON from the AI (urgency_tactics, impersonation_quality, etc.)
    """
    system_prompt = load_prompt("fraud_analysis")
    user_message = f"Content type: {content_type}\n\nContent to analyze:\n{content}"

    raw = call_ai("analysis", system_prompt, user_message, max_tokens=1500)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw, "parse_error": True}


def build_forensic_event(ai_result: dict) -> dict:
    """
    Convert the AI analysis JSON into a ForensicCheckEvent for SSE streaming.
    Derives a score from the AI's sub-scores and picks the most informative detail.
    """
    if ai_result.get("parse_error"):
        return {
            "check": "content_ai", "status": "warning",
            "title": "AI content analysis",
            "detail": "AI returned unexpected format.",
            "score": None,
        }

    # Average the fraud-indicator sub-scores (higher = more fraudulent)
    fraud_indicators = [
        ai_result.get("urgency_tactics", {}).get("score", 0) if isinstance(ai_result.get("urgency_tactics"), dict) else 0,
        ai_result.get("suspicious_requests", {}).get("score", 0) if isinstance(ai_result.get("suspicious_requests"), dict) else 0,
        ai_result.get("threat_indicators", {}).get("score", 0) if isinstance(ai_result.get("threat_indicators"), dict) else 0,
    ]
    legit_indicators = [
        ai_result.get("grammar_and_formatting", {}).get("score", 0.5) if isinstance(ai_result.get("grammar_and_formatting"), dict) else 0.5,
        ai_result.get("impersonation_quality", {}).get("score", 0.5) if isinstance(ai_result.get("impersonation_quality"), dict) else 0.5,
    ]

    fraud_avg = sum(fraud_indicators) / len(fraud_indicators) if fraud_indicators else 0
    # Legit score: low fraud signals + high grammar/professionalism = more likely legitimate
    legit_score = round((1 - fraud_avg) * 0.6 + (sum(legit_indicators) / len(legit_indicators)) * 0.4, 3)

    assessment = ai_result.get("overall_assessment", "")
    if isinstance(assessment, dict):
        detail = assessment.get("reasoning", str(assessment))
    else:
        detail = str(assessment)

    if legit_score < 0.3:
        status = "fail"
    elif legit_score > 0.7:
        status = "pass"
    else:
        status = "warning"

    return {
        "check": "content_ai",
        "status": status,
        "title": "AI content analysis",
        "detail": detail[:300] if detail else "Analysis complete.",
        "score": legit_score,
        "metadata": {
            "urgency": ai_result.get("urgency_tactics"),
            "impersonation": ai_result.get("impersonation_quality"),
            "suspicious_requests": ai_result.get("suspicious_requests"),
        },
    }
