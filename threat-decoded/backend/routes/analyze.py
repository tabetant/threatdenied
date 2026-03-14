"""
POST /api/analyze — SSE streaming forensic analysis
Phase 2 implementation target
"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
import uuid

from db import get_db
from models import AnalyzeRequest

router = APIRouter()


async def _run_analysis_stream(request: AnalyzeRequest, db: Session):
    """Placeholder SSE stream — Phase 2 will wire real analyzers."""
    report_id = str(uuid.uuid4())

    checks = [
        {"check": "sender", "status": "info", "title": "Sender verification", "detail": "Analysis pending — Phase 2", "score": None},
        {"check": "url", "status": "info", "title": "URL forensics", "detail": "Analysis pending — Phase 2", "score": None},
        {"check": "content_ai", "status": "info", "title": "AI content analysis", "detail": "Analysis pending — Phase 2", "score": None},
        {"check": "template", "status": "info", "title": "Template matching", "detail": "Analysis pending — Phase 2", "score": None},
        {"check": "campaign", "status": "info", "title": "Campaign linkage", "detail": "Analysis pending — Phase 2", "score": None},
        {"check": "verdict", "status": "inconclusive", "confidence": 0.0, "report_id": report_id},
    ]

    for event in checks:
        yield f"data: {json.dumps(event)}\n\n"


@router.post("/analyze")
async def analyze(request: AnalyzeRequest, db: Session = Depends(get_db)):
    return StreamingResponse(
        _run_analysis_stream(request, db),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
