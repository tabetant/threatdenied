"""
AI-powered test phishing email generator.
Phase 5 implementation target.
"""
import json
from ai.client import call_ai, load_prompt


def generate_test_emails(count: int, difficulty: str, avoid_types: list[str]) -> list[dict]:
    system_prompt = load_prompt("phish_generator")
    user_message = (
        f"Generate {count} test emails. Difficulty: {difficulty}. "
        f"Avoid these attack types: {', '.join(avoid_types) if avoid_types else 'none'}. "
        "Mix phishing and legitimate emails. Return a JSON array."
    )

    raw = call_ai("generation", system_prompt, user_message, max_tokens=4000)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []
