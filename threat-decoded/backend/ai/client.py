import anthropic
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Model routing: save credits by using the right model for each task
MODELS = {
    "analysis":   "claude-sonnet-4-20250514",   # Fraud analysis, content AI
    "generation": "claude-sonnet-4-20250514",   # Test email generation, alerts
    "chat":       "claude-sonnet-4-20250514",   # Conversational follow-up
    "coaching":   "claude-haiku-4-5-20251001",  # Training feedback (simpler)
    "scoring":    "claude-haiku-4-5-20251001",  # Flag evaluation (simpler)
    "clustering": "claude-sonnet-4-20250514",   # Campaign analysis
}


def call_ai(task_type: str, system_prompt: str, user_message: str, max_tokens: int = 1024) -> str:
    model = MODELS.get(task_type, "claude-sonnet-4-20250514")
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


def load_prompt(name: str) -> str:
    """Load a system prompt from backend/prompts/{name}.txt"""
    import os
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", f"{name}.txt")
    with open(os.path.abspath(prompt_path), "r") as f:
        return f.read().strip()
