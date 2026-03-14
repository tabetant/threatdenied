"""
GET  /api/training/emails/{user_id}
GET  /api/training/feedback/{submission_id}
POST /api/training/generate-test
POST /api/training/flag/{test_email_id}
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import json
import uuid

from db import get_db, Submission, TestEmail, User
from models import GenerateTestRequest, FlagTestEmailRequest, TestEmailSummary

from ai.training_coach import generate_feedback
from ai.phish_generator import generate_test_emails
from ai.scoring_judge import judge_flag

router = APIRouter()


@router.get("/training/emails/{user_id}")
def list_test_emails(user_id: str, db: Session = Depends(get_db)):
    """List all test emails for a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    emails = (
        db.query(TestEmail)
        .filter(TestEmail.user_id == user_id)
        .order_by(TestEmail.sent_at.desc())
        .all()
    )
    return [
        {
            "id": e.id,
            "type": e.type,
            "subject": e.subject,
            "body": e.body,
            "from_address": e.from_address,
            "difficulty": e.difficulty,
            "was_flagged": e.was_flagged,
            "flagged_at": e.flagged_at.isoformat() if e.flagged_at else None,
            "ai_feedback": json.loads(e.ai_feedback) if e.ai_feedback else None,
            "sent_at": e.sent_at.isoformat(),
        }
        for e in emails
    ]


@router.get("/training/feedback/{submission_id}")
def get_feedback(submission_id: str, db: Session = Depends(get_db)):
    """Get AI training feedback for a test email."""
    test_email = db.query(TestEmail).filter(TestEmail.id == submission_id).first()
    if not test_email:
        raise HTTPException(status_code=404, detail="Test email not found")

    # Return cached feedback if available
    if test_email.ai_feedback:
        return json.loads(test_email.ai_feedback)

    # Generate fresh feedback via AI
    was_phishing = test_email.type == "phishing"
    user_flagged = test_email.was_flagged if test_email.was_flagged is not None else False
    email_content = f"From: {test_email.from_address}\nSubject: {test_email.subject}\n\n{test_email.body}"

    result = generate_feedback(email_content, user_flagged, was_phishing)

    # Cache the feedback
    test_email.ai_feedback = json.dumps(result)
    db.commit()

    return result


@router.post("/training/generate-test")
def generate_test(request: GenerateTestRequest, db: Session = Depends(get_db)):
    """Generate new AI test phishing emails for a user."""
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    emails = generate_test_emails(request.count, request.difficulty, request.avoid_recent_types or [])

    saved = []
    for e in emails:
        test_email = TestEmail(
            id=str(uuid.uuid4()),
            user_id=request.user_id,
            type=e.get("type", "phishing"),
            subject=e.get("subject", "Test Email"),
            body=e.get("body", ""),
            from_address=e.get("from_address", "unknown@test.com"),
            difficulty=e.get("difficulty", request.difficulty),
            red_flags=json.dumps(e.get("red_flags", [])),
            why_legitimate=json.dumps(e.get("why_legitimate", [])),
        )
        db.add(test_email)
        saved.append({
            "id": test_email.id,
            "type": test_email.type,
            "subject": test_email.subject,
            "from_address": test_email.from_address,
            "difficulty": test_email.difficulty,
        })

    user.tests_sent += len(saved)
    db.commit()

    return {"test_emails": saved, "count": len(saved)}


@router.post("/training/flag/{test_email_id}")
def flag_test_email(test_email_id: str, request: FlagTestEmailRequest, db: Session = Depends(get_db)):
    """User flags a test email as phishing or legitimate. AI judges and provides feedback."""
    test_email = db.query(TestEmail).filter(TestEmail.id == test_email_id).first()
    if not test_email:
        raise HTTPException(status_code=404, detail="Test email not found")

    if test_email.was_flagged is not None:
        raise HTTPException(status_code=400, detail="This email has already been flagged")

    user = db.query(User).filter(User.id == test_email.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Record the flag
    test_email.was_flagged = request.flagged_as_phishing
    test_email.flagged_at = datetime.utcnow()

    # Determine correctness
    was_phishing = test_email.type == "phishing"
    user_correct = request.flagged_as_phishing == was_phishing

    # Call scoring judge for points
    submission_data = {
        "type": test_email.type,
        "subject": test_email.subject,
        "body": test_email.body,
        "from_address": test_email.from_address,
        "red_flags": test_email.red_flags,
    }
    user_verdict = "fraud" if request.flagged_as_phishing else "legitimate"
    judge_result = judge_flag(submission_data, user_verdict)

    points_delta = judge_result.get("points_delta", 10 if user_correct else -5)

    # Update user stats
    user.reward_points = max(0, user.reward_points + points_delta)
    if user_correct:
        user.tests_flagged_correctly += 1
        user.current_streak += 1
    else:
        user.current_streak = 0

    # Recalculate accuracy
    total_flagged = db.query(TestEmail).filter(
        TestEmail.user_id == user.id,
        TestEmail.was_flagged.isnot(None),
    ).count()
    if total_flagged > 0:
        user.accuracy_pct = round((user.tests_flagged_correctly / total_flagged) * 100, 1)

    # Generate training feedback
    email_content = f"From: {test_email.from_address}\nSubject: {test_email.subject}\n\n{test_email.body}"
    feedback = generate_feedback(email_content, request.flagged_as_phishing, was_phishing)

    # Cache feedback
    test_email.ai_feedback = json.dumps(feedback)
    db.commit()

    return {
        "correct": user_correct,
        "points_delta": points_delta,
        "new_points": user.reward_points,
        "new_streak": user.current_streak,
        "accuracy_pct": user.accuracy_pct,
        "feedback": feedback,
    }
