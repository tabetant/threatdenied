from fastapi import APIRouter, Depends
from database import get_db, Submission, now_est
from services.email_sender import send_reply
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/queue")
def get_review_queue(db=Depends(get_db)):
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
def submit_review(submission_id: str, body: dict, db=Depends(get_db)):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        return {"error": "Not found"}

    verdict = body.get("verdict")
    submission.reviewer_verdict = verdict
    submission.reviewer_notes = body.get("notes", "")
    submission.reviewed_at = now_est()
    submission.status = "reviewed"
    db.commit()  # Save verdict first, before attempting email

    # Send reply separately so a mail failure doesn't break the verdict save
    try:
        if verdict == "fraud":
            summary = "A TD analyst has reviewed this email and confirmed it is FRAUDULENT. Do not interact with this email or its sender."
        elif verdict == "legitimate":
            summary = "A TD analyst has reviewed this email and confirmed it is LEGITIMATE and was sent by TD Bank."
        else:
            summary = "A TD analyst has reviewed this email."

        send_reply(
            to=submission.forwarded_by,
            verdict=verdict,
            original_subject=submission.original_subject or "",
            original_body=submission.original_body or "",
            original_sender=submission.original_sender or "unknown",
            analysis_summary=summary
        )
        submission.reply_sent = True
        submission.reply_sent_at = now_est()
        db.commit()
        logger.info(f"Reply sent for submission {submission_id} verdict={verdict}")
    except Exception as e:
        logger.error(f"Failed to send reply for {submission_id}: {e}")
        return {"status": "reviewed", "verdict": verdict, "reply_error": str(e)}

    return {"status": "reviewed", "verdict": verdict}


@router.get("/api/history")
def get_history(db=Depends(get_db)):
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
