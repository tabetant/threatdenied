import anthropic
import json
import os

from config import ANTHROPIC_API_KEY
from fraud_prompt import FRAUD_ANALYSIS_PROMPT

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(_HERE, "..", "..", "data")


def analyze_email(sender: str, subject: str, body: str, headers: str = None) -> dict:
    known_senders = json.load(open(os.path.join(_DATA, "td_known_senders.json")))
    td_templates = json.load(open(os.path.join(_DATA, "td_templates.json")))

    user_message = f"""Analyze this email forwarded to TD Bank for fraud verification.

SENDER: {sender}
SUBJECT: {subject}
HEADERS: {headers or "Not available"}

BODY:
---
{body}
---

TD BANK KNOWN LEGITIMATE SENDERS:
{json.dumps(known_senders, indent=2)}

TD BANK REAL COMMUNICATION TEMPLATES:
{json.dumps(td_templates, indent=2)}

Return your analysis as JSON."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        system=FRAUD_ANALYSIS_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    raw = response.content[0].text
    cleaned = raw.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    try:
        return json.loads(cleaned.strip())
    except json.JSONDecodeError:
        return {
            "parse_error": True,
            "raw_response": raw,
            "sender_check": {
                "is_known_td_sender": False, "is_lookalike_domain": False,
                "display_name_mismatch": False, "spf_dkim_status": "unavailable", "red_flags": []
            },
            "url_analysis": {
                "urls_found": [], "has_lookalike_urls": False, "has_new_domains": False,
                "has_url_shorteners": False, "has_http_only": False, "high_risk_urls": [], "red_flags": []
            },
            "content_analysis": {
                "urgency_score": 5, "threat_level": "mild", "personal_info_requested": [],
                "grammar_quality": "unknown", "template_similarity": 40, "template_deviations": [],
                "emotional_manipulation": [], "call_to_action": "unknown",
                "call_to_action_legitimate": None, "red_flags": []
            },
            "verdict": "suspicious",
            "confidence": 40,
            "summary": "Analysis could not be fully parsed. Routing to human review."
        }
