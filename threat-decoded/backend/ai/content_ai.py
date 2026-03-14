"""
Claude-powered fraud content analysis.
Phase 2 implementation target.
"""
import json
from ai.client import call_ai, load_prompt


def analyze_content(content: str, content_type: str) -> dict:
    """
    Send content to Claude for forensic fraud analysis.
    Returns structured JSON with urgency_tactics, impersonation_quality, etc.
    """
    system_prompt = load_prompt("fraud_analysis")
    user_message = f"Content type: {content_type}\n\nContent to analyze:\n{content}"

    raw = call_ai("analysis", system_prompt, user_message, max_tokens=1500)
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {"raw": raw, "parse_error": True}

    return result
