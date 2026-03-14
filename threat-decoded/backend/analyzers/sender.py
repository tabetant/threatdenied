"""
Sender verification — checks submitted sender against known TD numbers/emails.
Phase 2 implementation target.
"""
import json
import os
import re


def load_known_senders() -> dict:
    path = os.path.join(os.path.dirname(__file__), "../../data/td_known_senders.json")
    with open(os.path.abspath(path)) as f:
        return json.load(f)


def check_sender(content: str, content_type: str) -> dict:
    """
    Extract sender info from content and check against TD's known list.
    Returns ForensicCheckEvent dict.
    """
    known = load_known_senders()

    # Extract email domain or phone number
    email_match = re.search(r"[\w.+-]+@([\w.-]+\.\w+)", content)
    phone_match = re.search(r"\b(\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})\b", content)

    if email_match:
        domain = email_match.group(1).lower()
        if domain in known.get("email_domains", []):
            return {"check": "sender", "status": "pass", "title": "Sender verification",
                    "detail": f"Domain @{domain} is a verified TD domain.", "score": 1.0}
        else:
            return {"check": "sender", "status": "fail", "title": "Sender verification",
                    "detail": f"Domain @{domain} is NOT a known TD domain.", "score": 0.0}

    if phone_match:
        number = re.sub(r"\D", "", phone_match.group(1))
        if number in known.get("phone_numbers", []):
            return {"check": "sender", "status": "pass", "title": "Sender verification",
                    "detail": "Phone number matches a known TD short code.", "score": 1.0}
        else:
            return {"check": "sender", "status": "warning", "title": "Sender verification",
                    "detail": "Phone number not in TD's registered sender list.", "score": 0.3}

    return {"check": "sender", "status": "info", "title": "Sender verification",
            "detail": "No sender identifier found in submission.", "score": None}
