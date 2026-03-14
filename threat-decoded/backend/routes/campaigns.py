"""GET /api/campaigns  |  GET /api/campaigns/brief/{id}"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db, Campaign

router = APIRouter()


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
    """AI-generated threat intelligence brief — Phase 6"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Phase 6: call ai/campaign_analyst.py here
    return {
        "campaign_id": campaign_id,
        "ai_summary": "AI campaign brief — Phase 6 implementation pending.",
        "recommended_alert": campaign.customer_alert or "Alert pending.",
        "severity": campaign.severity,
    }
