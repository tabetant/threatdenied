"""
Campaign linkage — hashes submission content and matches against known clusters.
Phase 2 implementation target.
"""
import hashlib
import re
from sqlalchemy.orm import Session
from db import Campaign, Submission


def normalize(content: str) -> str:
    """Strip dynamic parts (URLs, phone numbers, amounts) for stable hashing."""
    text = re.sub(r"https?://\S+", "URL", content)
    text = re.sub(r"\$[\d,]+\.?\d*", "AMOUNT", text)
    text = re.sub(r"\b\d{3,}\b", "NUM", text)
    return text.lower().strip()


def content_hash(content: str) -> str:
    normalized = normalize(content)
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def check_campaign(content: str, db: Session) -> dict:
    chash = content_hash(content)

    # Look for existing submissions with same hash
    similar = db.query(Submission).filter(
        Submission.campaign_id.isnot(None)
    ).all()

    for sub in similar:
        if sub.content and content_hash(sub.content) == chash and sub.campaign_id:
            campaign = db.query(Campaign).filter(Campaign.id == sub.campaign_id).first()
            if campaign:
                return {
                    "check": "campaign", "status": "fail", "title": "Campaign linkage",
                    "detail": f"Matches known campaign: '{campaign.label}' ({campaign.report_count} reports).",
                    "score": 0.1,
                    "metadata": {"campaign_id": campaign.id, "campaign_label": campaign.label,
                                 "report_count": campaign.report_count},
                }

    return {
        "check": "campaign", "status": "info", "title": "Campaign linkage",
        "detail": "No matching campaign cluster found. Content hash logged for future matching.",
        "score": None,
        "metadata": {"content_hash": chash},
    }
