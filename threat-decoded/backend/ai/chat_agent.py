"""
Claude-powered conversational chat about a fraud verdict.
Phase 3 implementation target.
"""
import json
from ai.client import call_ai, load_prompt


def chat_about_report(report: dict, message: str, history: list[dict]) -> dict:
    system_prompt = load_prompt("chat_agent")

    # Build context from the report
    report_context = json.dumps(report, indent=2, default=str)
    conversation = "\n".join([
        f"{m['role'].upper()}: {m['content']}" for m in history
    ])

    user_message = (
        f"Forensic report:\n{report_context}\n\n"
        f"{'Conversation so far:' + chr(10) + conversation + chr(10) + chr(10) if history else ''}"
        f"Customer question: {message}"
    )

    raw = call_ai("chat", system_prompt, user_message, max_tokens=1000)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"response": raw, "suggested_followups": []}
