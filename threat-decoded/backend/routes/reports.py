"""GET /api/report/{id}"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from db import get_db, Submission

router = APIRouter()


@router.get("/report/{report_id}")
def get_report(report_id: str, db: Session = Depends(get_db)):
    sub = db.query(Submission).filter(Submission.id == report_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Report not found")

    def _parse(field):
        try:
            return json.loads(field) if field else None
        except Exception:
            return field

    return {
        "id": sub.id,
        "type": sub.type,
        "content": sub.content,
        "verdict": sub.verdict,
        "confidence": sub.confidence,
        "sender_result": _parse(sub.sender_result),
        "url_result": _parse(sub.url_result),
        "content_ai_result": _parse(sub.content_ai_result),
        "template_result": _parse(sub.template_result),
        "campaign_result": _parse(sub.campaign_result),
        "campaign_id": sub.campaign_id,
        "submitted_at": sub.submitted_at.isoformat(),
    }
