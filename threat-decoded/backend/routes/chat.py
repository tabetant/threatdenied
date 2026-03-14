"""POST /api/chat — AI conversational follow-up about a verdict"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db, Submission
from models import ChatRequest
from ai.chat_agent import chat_about_report

router = APIRouter()


def _submission_to_report(sub: Submission) -> dict:
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
    }


@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    sub = db.query(Submission).filter(Submission.id == request.report_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Report not found")

    report = _submission_to_report(sub)

    try:
        result = chat_about_report(report, request.message, request.history or [])
    except Exception as e:
        result = {
            "response": f"I'm unable to respond right now. If you believe this is fraud, call TD at 1-866-222-3456.",
            "suggested_followups": ["What should I do with this message?", "How do I report this?"],
        }

    return result
