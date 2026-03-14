import json


def get_step3_prompt(content: str, content_type: str, td_templates: dict, step1_result: dict, step2_result: dict) -> tuple[str, str]:
    system = """You are a content analysis specialist at TD Bank. Your ONLY job is to analyze the BODY TEXT of the submitted message for fraud indicators.

You are checking:
1. URGENCY: Does the message create artificial urgency? ("Act now", "Your account will be suspended", "Immediate action required")
2. THREAT LANGUAGE: Does it threaten consequences for inaction? ("Your account will be closed", "Legal action")
3. PERSONAL INFO REQUESTS: Does it ask for passwords, PINs, SINs, full card numbers, or other sensitive data? (TD NEVER asks for these via email/SMS)
4. GRAMMAR & SPELLING: Are there grammatical errors, unusual phrasing, or formatting inconsistencies that don't match professional bank communications?
5. TEMPLATE MATCH: Does this message match how TD Bank actually communicates? Compare against the TD communication templates provided.
6. IMPERSONATION QUALITY: How convincingly does this impersonate TD?
7. CALL TO ACTION: What is the message asking the user to do? Is that consistent with legitimate TD communications?
8. EMOTIONAL MANIPULATION: Is the message designed to make the reader panic, feel greedy, or feel obligated?

You also have results from Steps 1 and 2 to provide context.

Return ONLY valid JSON with this exact structure:
{
  "step": "body_analysis",
  "urgency_score": 0-10,
  "threat_level": "none" or "mild" or "moderate" or "severe",
  "personal_info_requested": ["list of sensitive data types requested, or empty"],
  "grammar_quality": "professional" or "acceptable" or "poor" or "very_poor",
  "grammar_issues": ["specific examples of grammar/spelling problems"],
  "template_match": {
    "closest_td_template": "name of the closest matching TD template or 'no_match'",
    "similarity_score": 0-100,
    "deviations": ["specific differences from legitimate TD communications"]
  },
  "impersonation_sophistication": "low" or "medium" or "high" or "very_high",
  "call_to_action": "what the message is asking the user to do",
  "call_to_action_legitimate": true/false,
  "emotional_manipulation_tactics": ["list of tactics used"],
  "red_flags": ["all body-content red flags"],
  "verdict": "fraud" or "legitimate" or "suspicious",
  "confidence": 0-100,
  "detail": "2-3 sentence explanation of body analysis findings"
}"""

    user = f"""Content type: {content_type}

Submitted content:
---
{content}
---

TD Bank's communication templates:
{json.dumps(td_templates, indent=2)}

Previous analysis — Step 1 (Header/Sender):
{json.dumps(step1_result, indent=2)}

Previous analysis — Step 2 (URL Forensics):
{json.dumps(step2_result, indent=2)}

Analyze the body content and return your JSON verdict."""

    return system, user
