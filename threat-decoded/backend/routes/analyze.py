"""
POST /api/analyze — SSE streaming forensic analysis
Runs 5 checks sequentially, streaming each result as it completes.
Final event is the aggregated verdict, which is saved to the DB.
"""
import asyncio
import json
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from db import get_db, Submission
from models import AnalyzeRequest
from verdict import aggregate
from analyzers.sender import check_sender
from analyzers.url_forensics import check_urls
from analyzers.template_match import check_template
from analyzers.campaign import check_campaign, content_hash
from ai.content_ai import analyze_content, build_forensic_event

router = APIRouter()


async def _stream(request: AnalyzeRequest, db: Session):
    report_id = request.report_id or str(uuid.uuid4())
    checks_done = []

    # ── 1. Sender verification (fast, no AI) ──────────────────────────────────
    sender_result = check_sender(request.content, request.type)
    checks_done.append(sender_result)
    yield f"data: {json.dumps(sender_result)}\n\n"
    await asyncio.sleep(0)

    # ── 2. URL forensics (fast, no AI) ────────────────────────────────────────
    url_result = check_urls(request.content)
    checks_done.append(url_result)
    yield f"data: {json.dumps(url_result)}\n\n"
    await asyncio.sleep(0)

    # ── 3. Template matching (fast, no AI) ────────────────────────────────────
    template_result = check_template(request.content)
    checks_done.append(template_result)
    yield f"data: {json.dumps(template_result)}\n\n"
    await asyncio.sleep(0)

    # ── 4. Campaign linkage (DB lookup, no AI) ────────────────────────────────
    campaign_result = check_campaign(request.content, db)
    checks_done.append(campaign_result)
    campaign_id = (campaign_result.get("metadata") or {}).get("campaign_id")
    campaign_report_count = (campaign_result.get("metadata") or {}).get("report_count")
    yield f"data: {json.dumps(campaign_result)}\n\n"
    await asyncio.sleep(0)

    # ── 5. AI content analysis (Claude API — slowest, yields last) ────────────
    try:
        ai_raw = analyze_content(request.content, request.type)
        content_event = build_forensic_event(ai_raw)
    except Exception as e:
        content_event = {
            "check": "content_ai", "status": "warning",
            "title": "AI content analysis",
            "detail": f"AI analysis unavailable: {str(e)[:120]}",
            "score": None,
        }
        ai_raw = {}
    checks_done.append(content_event)
    yield f"data: {json.dumps(content_event)}\n\n"
    await asyncio.sleep(0)

    # ── Verdict ───────────────────────────────────────────────────────────────
    verdict_data = aggregate(checks_done)
    verdict_event = {
        "check": "verdict",
        "status": verdict_data["verdict"],
        "confidence": verdict_data["confidence"],
        "report_id": report_id,
        "campaign_id": campaign_id,
        "campaign_report_count": campaign_report_count,
    }
    yield f"data: {json.dumps(verdict_event)}\n\n"

    # ── Persist to DB ─────────────────────────────────────────────────────────
    sub = Submission(
        id=report_id,
        user_id=request.user_id,
        campaign_id=campaign_id,
        type=request.type,
        content=request.content,
        verdict=verdict_data["verdict"],
        confidence=verdict_data["confidence"],
        sender_result=json.dumps(sender_result),
        url_result=json.dumps(url_result),
        content_ai_result=json.dumps(ai_raw),
        template_result=json.dumps(template_result),
        campaign_result=json.dumps(campaign_result),
        submitted_at=datetime.utcnow(),
        is_test_email=False,
    )
    db.add(sub)
    db.commit()


@router.post("/analyze")
async def analyze(request: AnalyzeRequest, db: Session = Depends(get_db)):
    return StreamingResponse(
        _stream(request, db),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
