"""POST /api/chat — AI conversational follow-up about a verdict"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db, Submission
from models import ChatRequest

router = APIRouter()


@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Phase 3 implementation target — calls ai/chat_agent.py"""
    sub = db.query(Submission).filter(Submission.id == request.report_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Report not found")

    # Phase 3: replace stub with ai/chat_agent.py call
    return {
        "response": "Chat agent coming in Phase 3. Your report has been received.",
        "suggested_followups": [
            "What should I do with this message?",
            "Has anyone else reported this?",
            "How can I protect myself?",
        ],
    }
