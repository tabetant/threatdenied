"""
POST /api/analyze — SSE streaming 4-step forensic analysis
Each step is a Claude API call; results stream as SSE events.
"""
import json
import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from db import get_db, Submission, Campaign
from models import AnalyzeRequest
from services.llm import call_claude, compute_weighted_verdict
from prompts.step1_header import get_step1_prompt
from prompts.step2_links import get_step2_prompt
from prompts.step3_body import get_step3_prompt
from prompts.step4_campaign import get_step4_prompt

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(_HERE, "..", "..", "data")

router = APIRouter()

STEP_MESSAGES = {
    "header_analysis": "Analyzing sender information...",
    "url_forensics": "Investigating links and URLs...",
    "body_analysis": "Scanning message content...",
    "campaign_matching": "Cross-referencing fraud database...",
}


async def _stream(request: AnalyzeRequest, db: Session):
    report_id = request.report_id or str(uuid.uuid4())
    results = {}

    # Load reference data
    known_senders = json.load(open(os.path.join(_DATA, "td_known_senders.json")))
    td_templates = json.load(open(os.path.join(_DATA, "td_templates.json")))

    # ── Step 1: Header / Sender Analysis ──────────────────────────────────────
    yield f"event: step_processing\ndata: {json.dumps({'step': 'header_analysis', 'message': STEP_MESSAGES['header_analysis']})}\n\n"

    step1_sys, step1_user = get_step1_prompt(request.content, request.type, known_senders)
    results["step1_header"] = call_claude(step1_sys, step1_user)

    yield f"event: step_result\ndata: {json.dumps({'step': 'header_analysis', 'status': 'complete', 'result': results['step1_header']})}\n\n"

    # ── Step 2: URL Forensics ──────────────────────────────────────────────────
    yield f"event: step_processing\ndata: {json.dumps({'step': 'url_forensics', 'message': STEP_MESSAGES['url_forensics']})}\n\n"

    step2_sys, step2_user = get_step2_prompt(request.content, request.type, known_senders, results["step1_header"])
    results["step2_links"] = call_claude(step2_sys, step2_user)

    yield f"event: step_result\ndata: {json.dumps({'step': 'url_forensics', 'status': 'complete', 'result': results['step2_links']})}\n\n"

    # ── Step 3: Body Content Analysis ─────────────────────────────────────────
    yield f"event: step_processing\ndata: {json.dumps({'step': 'body_analysis', 'message': STEP_MESSAGES['body_analysis']})}\n\n"

    step3_sys, step3_user = get_step3_prompt(request.content, request.type, td_templates, results["step1_header"], results["step2_links"])
    results["step3_body"] = call_claude(step3_sys, step3_user)

    yield f"event: step_result\ndata: {json.dumps({'step': 'body_analysis', 'status': 'complete', 'result': results['step3_body']})}\n\n"

    # ── Step 4: Campaign Pattern Matching ─────────────────────────────────────
    yield f"event: step_processing\ndata: {json.dumps({'step': 'campaign_matching', 'message': STEP_MESSAGES['campaign_matching']})}\n\n"

    campaigns = db.query(Campaign).filter(Campaign.is_active == True).all()
    campaign_data = [
        {
            "id": c.id,
            "name": c.label,
            "description": c.tactics_summary or "",
            "pattern_signature": c.content_hash or "",
            "channel_type": c.attack_vector,
        }
        for c in campaigns
    ]

    step4_sys, step4_user = get_step4_prompt(request.content, request.type, campaign_data, results["step1_header"], results["step2_links"], results["step3_body"])
    results["step4_campaign"] = call_claude(step4_sys, step4_user)

    yield f"event: step_result\ndata: {json.dumps({'step': 'campaign_matching', 'status': 'complete', 'result': results['step4_campaign']})}\n\n"

    # ── Weighted Verdict ───────────────────────────────────────────────────────
    final_verdict = compute_weighted_verdict(results)

    # ── Persist to DB ─────────────────────────────────────────────────────────
    campaign_id = None
    step4 = results["step4_campaign"]

    if final_verdict["classification"] == "fraud":
        if step4.get("is_new_campaign"):
            new_campaign = Campaign(
                label=step4.get("suggested_campaign_name", "Unnamed Campaign"),
                attack_vector=request.type,
                tactics_summary=step4.get("suggested_campaign_description", ""),
                content_hash=step4.get("pattern_signature", ""),
                severity="high",
                report_count=1,
            )
            db.add(new_campaign)
            db.flush()
            campaign_id = new_campaign.id
        elif step4.get("matches_existing_campaign") and step4.get("matched_campaign_id"):
            campaign_id = step4.get("matched_campaign_id")
            matched = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if matched:
                matched.report_count += 1
                matched.last_seen = datetime.utcnow()

    sub = Submission(
        id=report_id,
        user_id=request.user_id,
        campaign_id=campaign_id,
        type=request.type,
        content=request.content,
        verdict=final_verdict["classification"],
        confidence=final_verdict["fraud_score"],
        sender_result=json.dumps(results["step1_header"]),
        url_result=json.dumps(results["step2_links"]),
        content_ai_result=json.dumps(results["step3_body"]),
        campaign_result=json.dumps(results["step4_campaign"]),
        template_result=json.dumps(final_verdict["signals_triggered"]),
        submitted_at=datetime.utcnow(),
        is_test_email=False,
    )
    db.add(sub)
    db.commit()

    # ── Stream final verdict + done ────────────────────────────────────────────
    final_result = {
        "submission_id": report_id,
        "report_id": report_id,
        "classification": final_verdict["classification"],
        "verdict": final_verdict["classification"],
        "fraud_score": final_verdict["fraud_score"],
        "confidence": final_verdict["confidence"],
        "signals_triggered": final_verdict["signals_triggered"],
        "signals_count": final_verdict["signals_count"],
        "score_breakdown": final_verdict["score_breakdown"],
        "step_verdicts": final_verdict["step_verdicts"],
        "campaign_id": campaign_id,
    }

    yield f"event: verdict\ndata: {json.dumps(final_result)}\n\n"
    yield f"event: done\ndata: {json.dumps({'submission_id': report_id, 'report_id': report_id})}\n\n"


@router.post("/analyze")
async def analyze(request: AnalyzeRequest, db: Session = Depends(get_db)):
    return StreamingResponse(
        _stream(request, db),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
