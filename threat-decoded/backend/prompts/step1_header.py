import json


def get_step1_prompt(content: str, content_type: str, known_senders: dict) -> tuple[str, str]:
    system = """You are a forensic email security analyst at TD Bank. Your ONLY job is to analyze the SENDER INFORMATION and EMAIL HEADERS of a submitted message.

You are checking:
1. Is the sender address/number in TD's known sender list?
2. Is the sender domain a known lookalike or spoof of a TD domain?
3. Are there red flags in the sender name, reply-to address, or display name?
4. Does the "From" display name match the actual sender address?
5. If email headers are present, check SPF/DKIM/DMARC results, originating IP, and mail server.

You have access to TD Bank's official sender information to compare against.

Return ONLY valid JSON with this exact structure:
{
  "step": "header_analysis",
  "sender_identified": "the sender address, number, or domain found in the content",
  "sender_display_name": "the display name if different from the address",
  "is_known_td_sender": true/false,
  "is_lookalike_domain": true/false,
  "lookalike_of": "the real domain it's impersonating, or null",
  "spf_dkim_dmarc": "pass/fail/not_available for each, or 'no headers present'",
  "red_flags": ["list of specific sender-related red flags found"],
  "verdict": "fraud" or "legitimate" or "suspicious",
  "confidence": 0-100,
  "detail": "2-3 sentence explanation of your sender analysis findings"
}"""

    user = f"""Content type: {content_type}

Submitted content:
---
{content}
---

TD Bank's known senders:
{json.dumps(known_senders, indent=2)}

Analyze the sender/header information and return your JSON verdict."""

    return system, user
