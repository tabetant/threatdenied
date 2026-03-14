"""GET /api/profile/{user_id}"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db, User

router = APIRouter()


@router.get("/profile/{user_id}")
def get_profile(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "reward_points": user.reward_points,
        "current_streak": user.current_streak,
        "tests_sent": user.tests_sent,
        "tests_flagged_correctly": user.tests_flagged_correctly,
        "real_submissions": user.real_submissions,
        "accuracy_pct": user.accuracy_pct,
    }
