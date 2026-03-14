"""
AI-powered training feedback generator.
Phase 5 implementation target.
"""
import json
from ai.client import call_ai, load_prompt


def generate_feedback(email_content: str, user_flagged: bool, was_phishing: bool) -> dict:
    system_prompt = load_prompt("training_coach")
    user_message = (
        f"Test email content:\n{email_content}\n\n"
        f"User flagged as phishing: {user_flagged}\n"
        f"Was actually phishing: {was_phishing}"
    )

    raw = call_ai("coaching", system_prompt, user_message, max_tokens=800)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw, "parse_error": True}
