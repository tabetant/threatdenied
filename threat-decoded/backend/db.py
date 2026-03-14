from sqlalchemy import (
    create_engine, Column, String, Float, Integer,
    Boolean, DateTime, Text, ForeignKey
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
from datetime import datetime
import uuid

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    reward_points = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    tests_sent = Column(Integer, default=0)
    tests_flagged_correctly = Column(Integer, default=0)
    real_submissions = Column(Integer, default=0)
    accuracy_pct = Column(Float, default=0.0)
    enrolled_training = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    submissions = relationship("Submission", back_populates="user")
    test_emails = relationship("TestEmail", back_populates="user")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    label = Column(String, nullable=False)
    attack_vector = Column(String, nullable=False)  # sms | email | url
    severity = Column(String, default="medium")     # low | medium | high | critical
    report_count = Column(Integer, default=0)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    tactics_summary = Column(Text, nullable=True)
    customer_alert = Column(Text, nullable=True)
    content_hash = Column(String, nullable=True)    # for clustering

    submissions = relationship("Submission", back_populates="campaign")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=True)
    type = Column(String, nullable=False)           # sms | email | url | screenshot
    content = Column(Text, nullable=False)
    verdict = Column(String, nullable=True)          # fraud | legitimate | inconclusive
    confidence = Column(Float, nullable=True)
    # Check results stored as JSON text
    sender_result = Column(Text, nullable=True)
    url_result = Column(Text, nullable=True)
    content_ai_result = Column(Text, nullable=True)
    template_result = Column(Text, nullable=True)
    campaign_result = Column(Text, nullable=True)
    # Geographic info (derived from submission context)
    city = Column(String, nullable=True)
    province = Column(String, nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    is_test_email = Column(Boolean, default=False)

    user = relationship("User", back_populates="submissions")
    campaign = relationship("Campaign", back_populates="submissions")


class TestEmail(Base):
    __tablename__ = "test_emails"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)            # phishing | legitimate
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    from_address = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)      # easy | medium | hard
    red_flags = Column(Text, nullable=True)          # JSON array string
    why_legitimate = Column(Text, nullable=True)     # JSON array string
    was_flagged = Column(Boolean, nullable=True)     # null = not yet reviewed
    flagged_at = Column(DateTime, nullable=True)
    ai_feedback = Column(Text, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="test_emails")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
