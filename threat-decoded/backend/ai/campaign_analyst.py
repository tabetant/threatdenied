"""
AI-powered campaign clustering and threat intelligence.
Phase 6 implementation target.
"""
import json
from ai.client import call_ai, load_prompt


def analyze_campaign(submissions: list[dict]) -> dict:
    system_prompt = load_prompt("campaign_analyst")
    user_message = f"Submission cluster ({len(submissions)} reports):\n{json.dumps(submissions, indent=2, default=str)}"

    raw = call_ai("clustering", system_prompt, user_message, max_tokens=1500)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw, "parse_error": True}
