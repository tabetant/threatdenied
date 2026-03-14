"""
Claude-powered scoring judge for edge-case flag evaluation.
Phase 5 implementation target.
"""
import json
from ai.client import call_ai, load_prompt


def judge_flag(submission: dict, user_verdict: str) -> dict:
    """
    Evaluate whether a user's flag was correct, handling edge cases.
    Returns: {correct: bool, points_delta: int, explanation: str}
    """
    system_prompt = (
        "You are a scoring judge for TD Bank's Threat Decoded program. "
        "A customer has flagged a submission as fraud or legitimate. "
        "Evaluate their verdict against the forensic evidence and return JSON: "
        "{\"correct\": bool, \"points_delta\": int, \"explanation\": string}. "
        "Points: +10 for correct fraud flag, +5 for correct legit, "
        "-5 for false fraud flag (flagging real TD comms), 0 for inconclusive."
    )
    user_message = (
        f"Submission: {json.dumps(submission, default=str)}\n"
        f"User verdict: {user_verdict}"
    )

    raw = call_ai("scoring", system_prompt, user_message, max_tokens=400)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"correct": False, "points_delta": 0, "explanation": raw}
