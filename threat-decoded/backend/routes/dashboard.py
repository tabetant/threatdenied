"""GET /api/dashboard/stats  |  GET /api/dashboard/trends"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, date, timedelta

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
        "total_submissions": total,
        "fraud_rate": fraud_rate,
        "active_campaigns": active_campaigns,
        "top_campaign": top.label if top else None,
        "geographic_data": [
            {"city": g.city, "province": g.province, "lat": g.lat, "lng": g.lng, "count": g.count}
            for g in geo_data
        ],
    }


@router.get("/dashboard/trends")
def get_trends(db: Session = Depends(get_db)):
    """Submission counts by verdict over the last 14 days."""
    cutoff = datetime.utcnow() - timedelta(days=14)

    rows = db.query(
        func.date(Submission.submitted_at).label("day"),
        func.sum(case((Submission.verdict == "fraud", 1), else_=0)).label("fraud"),
        func.sum(case((Submission.verdict == "legitimate", 1), else_=0)).label("legitimate"),
        func.sum(case((Submission.verdict == "inconclusive", 1), else_=0)).label("inconclusive"),
    ).filter(
        Submission.submitted_at >= cutoff
    ).group_by(func.date(Submission.submitted_at)).order_by("day").all()

    # Fill in missing days with zeros
    result = []
    for i in range(14):
        d = (date.today() - timedelta(days=13 - i)).isoformat()
        match = next((r for r in rows if str(r.day) == d), None)
        result.append({
            "date": d,
            "fraud": int(match.fraud) if match else 0,
            "legitimate": int(match.legitimate) if match else 0,
            "inconclusive": int(match.inconclusive) if match else 0,
        })

    return result
