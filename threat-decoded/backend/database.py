from sqlalchemy import create_engine, Column, String, Text, Float, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime, timezone, timedelta
from uuid import uuid4
import os

from dotenv import load_dotenv
load_dotenv()

EST = timezone(timedelta(hours=-5))


def now_est():
    return datetime.now(EST).replace(tzinfo=None)


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./threat_decoded.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_size=20,
    max_overflow=30,
    pool_recycle=300,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class Submission(Base):
    __tablename__ = "submissions_v2"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))

    # Who sent it to us
    forwarded_by = Column(String)

    # The original suspicious email
    original_sender = Column(String, nullable=True)
    original_subject = Column(String, nullable=True)
    original_body = Column(Text)
    original_headers = Column(Text, nullable=True)
    raw_email = Column(Text)

    # AI analysis
    ai_verdict = Column(String, nullable=True)
    ai_confidence = Column(Float, nullable=True)
    ai_fraud_score = Column(Float, nullable=True)
    ai_analysis = Column(Text, nullable=True)
    ai_signals = Column(Text, nullable=True)

    # Status
    status = Column(String, default="pending")

    # Human review
    reviewer_verdict = Column(String, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    # Reply tracking
    reply_sent = Column(Boolean, default=False)
    reply_sent_at = Column(DateTime, nullable=True)

    # Timestamps
    received_at = Column(DateTime, default=now_est)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
