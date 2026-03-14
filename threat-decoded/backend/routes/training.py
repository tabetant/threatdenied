"""
GET  /api/training/feedback/{submission_id}
POST /api/training/generate-test
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db, Submission, TestEmail
from models import GenerateTestRequest

router = APIRouter()


@router.get("/training/feedback/{submission_id}")
def get_feedback(submission_id: str, db: Session = Depends(get_db)):
    """Phase 5 implementation target — calls ai/training_coach.py"""
    sub = db.query(Submission).filter(Submission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    return {
        "was_test": sub.is_test_email,
        "user_was_correct": None,
        "ai_explanation": "Training coach coming in Phase 5.",
        "tips": ["Verify sender domains", "Check for urgency language", "When in doubt, don't click"],
        "difficulty": None,
    }


@router.post("/training/generate-test")
def generate_test(request: GenerateTestRequest, db: Session = Depends(get_db)):
    """Phase 5 implementation target — calls ai/phish_generator.py"""
    return {
        "test_emails": [],
        "message": "Test email generation coming in Phase 5.",
    }
