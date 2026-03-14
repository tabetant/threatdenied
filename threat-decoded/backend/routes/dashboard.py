"""GET /api/dashboard/stats"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date

from db import get_db, Submission, Campaign

router = APIRouter()


@router.get("/dashboard/stats")
def get_stats(db: Session = Depends(get_db)):
    today = date.today()

    total_today = db.query(func.count(Submission.id)).filter(
        func.date(Submission.submitted_at) == today
    ).scalar() or 0

    total = db.query(func.count(Submission.id)).scalar() or 0
    fraud_count = db.query(func.count(Submission.id)).filter(
        Submission.verdict == "fraud"
    ).scalar() or 0
    fraud_rate = round(fraud_count / total, 2) if total > 0 else 0.0

    active_campaigns = db.query(func.count(Campaign.id)).filter(
        Campaign.is_active == True
    ).scalar() or 0

    top = db.query(Campaign).filter(Campaign.is_active == True).order_by(
        Campaign.report_count.desc()
    ).first()

    geo_data = db.query(
        Submission.city, Submission.province, Submission.lat, Submission.lng,
        func.count(Submission.id).label("count")
    ).filter(
        Submission.lat.isnot(None)
    ).group_by(Submission.city, Submission.province, Submission.lat, Submission.lng).all()

    return {
        "total_submissions_today": total_today,
        "fraud_rate": fraud_rate,
        "active_campaigns": active_campaigns,
        "top_campaign": top.label if top else None,
        "geographic_data": [
            {"city": g.city, "province": g.province, "lat": g.lat, "lng": g.lng, "count": g.count}
            for g in geo_data
        ],
    }
