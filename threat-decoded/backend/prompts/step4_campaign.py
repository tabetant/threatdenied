import json


def get_step4_prompt(content: str, content_type: str, existing_campaigns: list, step1_result: dict, step2_result: dict, step3_result: dict) -> tuple[str, str]:
    system = """You are a threat intelligence analyst at TD Bank. Your job is to compare a newly submitted suspicious message against a DATABASE of known active fraud campaigns to determine if this submission is part of an existing campaign.

You are checking:
1. Does this submission share key characteristics with any existing campaign? (similar sender patterns, similar URLs, similar body text, similar call-to-action)
2. If it matches an existing campaign, which one and how confident are you?
3. If it does NOT match any existing campaign but is still fraud, could this be a NEW campaign that should be created?
4. What is the pattern signature of this submission that could be used to match future similar submissions?

You have:
- The submitted content
- Results from all 3 previous analysis steps
- A database of currently active fraud campaigns with their pattern signatures

Return ONLY valid JSON with this exact structure:
{
  "step": "campaign_matching",
  "matches_existing_campaign": true/false,
  "matched_campaign_id": "the campaign ID if matched, or null",
  "matched_campaign_name": "the campaign name if matched, or null",
  "match_confidence": 0-100,
  "match_reasoning": "why this matches or doesn't match",
  "is_new_campaign": true/false,
  "suggested_campaign_name": "if new campaign, suggest a descriptive name, or null",
  "suggested_campaign_description": "if new campaign, describe it, or null",
  "pattern_signature": "key identifying features that could match future similar submissions",
  "verdict": "fraud" or "legitimate" or "suspicious",
  "confidence": 0-100,
  "detail": "2-3 sentence explanation of campaign analysis findings"
}

IMPORTANT: If previous steps all say "legitimate", you can agree and return verdict "legitimate". Only match/create campaigns for fraud or suspicious content."""

    user = f"""Content type: {content_type}

Submitted content:
---
{content}
---

Existing active fraud campaigns in database:
{json.dumps(existing_campaigns, indent=2)}

Previous analysis — Step 1 (Header/Sender):
{json.dumps(step1_result, indent=2)}

Previous analysis — Step 2 (URL Forensics):
{json.dumps(step2_result, indent=2)}

Previous analysis — Step 3 (Body Content):
{json.dumps(step3_result, indent=2)}

Analyze for campaign patterns and return your JSON verdict."""

    return system, user
