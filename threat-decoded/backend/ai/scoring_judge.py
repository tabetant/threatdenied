"""
AI-powered scoring judge for edge-case flag evaluation.
Phase 5 implementation target.
"""
import json
from ai.client import call_ai, load_prompt


def judge_flag(submission: dict, user_verdict: str) -> dict:
    """
    Evaluate whether a user's flag was correct, handling edge cases.
    Returns: {correct: bool, points_delta: int, explanation: str}
    """
    system_prompt = load_prompt("scoring_judge")
    user_message = (
        f"Submission: {json.dumps(submission, default=str)}\n"
        f"User verdict: {user_verdict}"
    )

    raw = call_ai("scoring", system_prompt, user_message, max_tokens=400)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"correct": False, "points_delta": 0, "explanation": raw}
