"""GET /api/campaigns  |  GET /api/campaigns/brief/{id}"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db, Campaign, Submission
from ai.campaign_analyst import analyze_campaign
from ai.alert_writer import write_alert

router = APIRouter()

# In-memory cache for AI-generated briefs (hackathon-friendly, avoids repeat API calls)
_brief_cache: dict[str, dict] = {}


@router.get("/campaigns")
def list_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).filter(Campaign.is_active == True).order_by(Campaign.report_count.desc()).all()
    return [
        {
            "id": c.id,
            "label": c.label,
            "attack_vector": c.attack_vector,
            "severity": c.severity,
            "report_count": c.report_count,
            "first_seen": c.first_seen.isoformat(),
            "last_seen": c.last_seen.isoformat(),
            "is_active": c.is_active,
            "tactics_summary": c.tactics_summary,
            "customer_alert": c.customer_alert,
        }
        for c in campaigns
    ]


@router.get("/campaigns/brief/{campaign_id}")
def get_campaign_brief(campaign_id: str, db: Session = Depends(get_db)):
    """AI-generated threat intelligence brief for a campaign."""
    # Return cached brief if available
    if campaign_id in _brief_cache:
        return _brief_cache[campaign_id]

    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Gather submissions for this campaign
    submissions = (
        db.query(Submission)
        .filter(Submission.campaign_id == campaign_id)
        .limit(10)
        .all()
    )

    submissions_data = [
        {
            "type": s.type,
            "content": s.content[:300],
            "verdict": s.verdict,
            "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None,
            "city": s.city,
            "province": s.province,
        }
        for s in submissions
    ]

    # Call AI for campaign analysis
    try:
        analysis = analyze_campaign(submissions_data)
        ai_summary = analysis.get("tactics_summary", campaign.tactics_summary or "Analysis pending.")
    except Exception:
        ai_summary = campaign.tactics_summary or "AI analysis unavailable."

    # Call AI for customer-facing alert
    try:
        campaign_context = f"Campaign: {campaign.label}. Vector: {campaign.attack_vector}. Severity: {campaign.severity}. Summary: {ai_summary}"
        recommended_alert = write_alert(campaign_context)
    except Exception:
        recommended_alert = campaign.customer_alert or "Alert generation unavailable."

    result = {
        "campaign_id": campaign_id,
        "ai_summary": ai_summary,
        "recommended_alert": recommended_alert,
        "severity": campaign.severity,
    }

    # Cache the result
    _brief_cache[campaign_id] = result

    return result
