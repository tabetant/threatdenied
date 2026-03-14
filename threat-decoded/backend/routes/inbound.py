from fastapi import APIRouter, Request, BackgroundTasks
from services.email_parser import parse_inbound_email
from services.analyzer import analyze_email
from services.scorer import compute_verdict
from services.email_sender import send_reply
from database import get_db, Submission
from datetime import datetime
import json

router = APIRouter()


@router.post("/inbound")
async def receive_email(request: Request, background_tasks: BackgroundTasks):
    form = await request.form()
    parsed = parse_inbound_email(form)

    db = next(get_db())
    submission = Submission(
        forwarded_by=parsed["forwarded_by"],
        original_sender=parsed["original_sender"],
        original_subject=parsed["original_subject"],
        original_body=parsed["original_body"],
        original_headers=parsed["original_headers"],
        raw_email=parsed["raw_email"],
        status="pending"
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    background_tasks.add_task(process_submission, submission.id)
    return {"status": "received", "id": submission.id}


def process_submission(submission_id: str):
    db = next(get_db())
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        return

    try:
        ai_result = analyze_email(
            sender=submission.original_sender or "unknown",
            subject=submission.original_subject or "",
            body=submission.original_body or "",
            headers=submission.original_headers
        )

        verdict = compute_verdict(ai_result)

        submission.ai_verdict = verdict["classification"]
        submission.ai_confidence = verdict["confidence"]
        submission.ai_fraud_score = verdict["fraud_score"]
        submission.ai_analysis = json.dumps(ai_result)
        submission.ai_signals = json.dumps(verdict["signals_triggered"])

        if verdict["confidence"] >= 70:
            send_reply(
                to=submission.forwarded_by,
                verdict=verdict["classification"],
                original_subject=submission.original_subject or "",
                original_body=submission.original_body or "",
                original_sender=submission.original_sender or "unknown",
                analysis_summary=verdict["summary"]
            )
            submission.status = "auto_replied"
            submission.reply_sent = True
            submission.reply_sent_at = datetime.utcnow()
        else:
            submission.status = "needs_review"

    except Exception as e:
        submission.status = "needs_review"
        submission.ai_analysis = json.dumps({"error": str(e)})

    db.commit()
