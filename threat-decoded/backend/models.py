from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


# ── Submission / Analysis ────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    type: str                       # sms | email | url | screenshot
    content: str
    user_id: Optional[str] = None


class ForensicCheckEvent(BaseModel):
    check: str                      # sender | url | content_ai | template | campaign | verdict
    status: str                     # pass | fail | warning | info | fraud | legitimate | inconclusive
    title: str
    detail: str
    score: Optional[float] = None
    metadata: Optional[dict] = None


class VerdictEvent(BaseModel):
    check: str = "verdict"
    status: str                     # fraud | legitimate | inconclusive
    confidence: float
    report_id: str
    campaign_id: Optional[str] = None
    campaign_report_count: Optional[int] = None


# ── Report ───────────────────────────────────────────────────────────────────

class ReportResponse(BaseModel):
    id: str
    type: str
    content: str
    verdict: Optional[str]
    confidence: Optional[float]
    sender_result: Optional[Any]
    url_result: Optional[Any]
    content_ai_result: Optional[Any]
    template_result: Optional[Any]
    campaign_result: Optional[Any]
    campaign_id: Optional[str]
    submitted_at: datetime


# ── Campaign ─────────────────────────────────────────────────────────────────

class CampaignResponse(BaseModel):
    id: str
    label: str
    attack_vector: str
    severity: str
    report_count: int
    first_seen: datetime
    last_seen: datetime
    is_active: bool
    tactics_summary: Optional[str]
    customer_alert: Optional[str]


class CampaignBriefResponse(BaseModel):
    campaign_id: str
    ai_summary: str
    recommended_alert: str
    severity: str


# ── Profile ──────────────────────────────────────────────────────────────────

class ProfileResponse(BaseModel):
    id: str
    email: str
    name: str
    reward_points: int
    current_streak: int
    tests_sent: int
    tests_flagged_correctly: int
    real_submissions: int
    accuracy_pct: float


# ── Dashboard ────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_submissions_today: int
    fraud_rate: float
    active_campaigns: int
    top_campaign: Optional[str]
    geographic_data: List[dict]


# ── Chat ─────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    report_id: str
    message: str
    history: Optional[List[dict]] = []


class ChatResponse(BaseModel):
    response: str
    suggested_followups: List[str]


# ── Training ─────────────────────────────────────────────────────────────────

class TrainingFeedbackResponse(BaseModel):
    was_test: bool
    user_was_correct: Optional[bool]
    ai_explanation: str
    tips: List[str]
    difficulty: Optional[str]


class GenerateTestRequest(BaseModel):
    user_id: str
    count: int = 5
    difficulty: str = "medium"      # easy | medium | hard
    avoid_recent_types: Optional[List[str]] = []
