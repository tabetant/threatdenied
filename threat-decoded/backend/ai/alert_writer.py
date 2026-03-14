"""
Claude-powered customer-facing alert drafter.
Phase 6 implementation target.
"""
from ai.client import call_ai, load_prompt


def write_alert(campaign_summary: str) -> str:
    system_prompt = load_prompt("alert_writer")
    return call_ai("generation", system_prompt, campaign_summary, max_tokens=300)
