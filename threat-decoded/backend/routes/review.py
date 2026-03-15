from fastapi import APIRouter
from database import get_db, Submission
from services.email_sender import send_reply
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def _verdicts_compatible(v1: str, v2: str) -> bool:
    """Check if two verdicts are on the same side (both fraud-ish or both legit)."""
    v1, v2 = (v1 or "").lower(), (v2 or "").lower()
    if v1 == v2:
        return True
    if v1 in ("fraud", "suspicious") and v2 in ("fraud", "suspicious"):
        return True
    return False


@router.get("/api/queue")
def get_review_queue():
    db = next(get_db())
    pending = db.query(Submission).filter(Submission.status == "needs_review").order_by(Submission.received_at.desc()).all()
    return [{
        "id": s.id,
        "forwarded_by": s.forwarded_by,
        "original_sender": s.original_sender,
        "original_subject": s.original_subject,
        "original_body": s.original_body,
        "ai_verdict": s.ai_verdict,
        "ai_confidence": s.ai_confidence,
        "ai_fraud_score": s.ai_fraud_score,
        "ai_signals": json.loads(s.ai_signals) if s.ai_signals else [],
        "ai_summary": json.loads(s.ai_analysis).get("summary", "") if s.ai_analysis else "",
        "received_at": s.received_at.isoformat(),
    } for s in pending]


@router.post("/api/review/{submission_id}")
def submit_review(submission_id: str, body: dict):
    db = next(get_db())
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        return {"error": "Not found"}

    verdict = body.get("verdict")
    submission.reviewer_verdict = verdict
    submission.reviewer_notes = body.get("notes", "")
    submission.reviewed_at = datetime.now()
    submission.status = "reviewed"
    db.commit()  # Save verdict first, before attempting email

    # Send reply separately so a mail failure doesn't break the verdict save
    try:
        analysis = json.loads(submission.ai_analysis) if submission.ai_analysis else {}
        ai_summary = analysis.get("summary", "")

        # If the analyst's verdict differs from the AI verdict, don't send
        # the AI's summary (it would contradict the verdict). Use a clean
        # analyst-reviewed message instead.
        ai_verdict = submission.ai_verdict or ""
        if ai_summary and _verdicts_compatible(verdict, ai_verdict):
            summary = ai_summary
        else:
            summary = "This email has been reviewed by a TD fraud analyst who has determined the final verdict."

        send_reply(
            to=submission.forwarded_by,
            verdict=verdict,
            original_subject=submission.original_subject or "",
            original_body=submission.original_body or "",
            original_sender=submission.original_sender or "unknown",
            analysis_summary=summary
        )
        submission.reply_sent = True
        submission.reply_sent_at = datetime.now()
        db.commit()
        logger.info(f"Reply sent for submission {submission_id} verdict={verdict}")
    except Exception as e:
        logger.error(f"Failed to send reply for {submission_id}: {e}")
        return {"status": "reviewed", "verdict": verdict, "reply_error": str(e)}

    return {"status": "reviewed", "verdict": verdict}


@router.get("/api/history")
def get_history():
    db = next(get_db())
    recent = db.query(Submission).filter(
        Submission.status.in_(["auto_replied", "reviewed"])
    ).order_by(Submission.received_at.desc()).limit(50).all()
    return [{
        "id": s.id,
        "forwarded_by": s.forwarded_by,
        "original_sender": s.original_sender,
        "original_subject": s.original_subject,
        "verdict": s.reviewer_verdict or s.ai_verdict,
        "fraud_score": s.ai_fraud_score,
        "status": s.status,
        "received_at": s.received_at.isoformat(),
    } for s in recent]
