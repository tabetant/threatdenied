"""
Seed script: populates the DB with demo data.
5 campaigns + 60 submissions + 5 demo users.
Run: python seed.py
"""
import json
import os
import sys
import uuid
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from db import init_db, SessionLocal, User, Campaign, Submission, TestEmail

# ── Sample content per campaign ──────────────────────────────────────────────

SAMPLE_CONTENT = {
    "GTA Visa Credit Limit SMS Campaign": [
        "TD Alert: Congratulations! Your TD Visa credit limit has been pre-approved for an increase to $15,000. Verify your identity to activate: https://td-secure-verify.ca/activate",
        "TD Bank: Your credit limit increase to $12,500 is ready. Click to confirm: https://td-limit-upgrade.ca/confirm?ref=74821",
        "From TD: You qualify for a $18,000 Visa limit boost. Act now before offer expires: http://td-offers-ca.com/credit",
        "TD VISA ALERT: Credit limit increase pre-approved. Tap to verify and activate https://tdvisa-secure.ca/upgrade",
    ],
    "Fake Interac e-Transfer Email Campaign": [
        "From: TD Canada Trust <notifications@td-etransfer-alert.com>\nSubject: You've received an Interac e-Transfer\n\nYou've received $500.00 from John Smith. To deposit your money, click here: https://td-etransfer-alert.com/deposit\nThis transfer will expire in 24 hours.",
        "From: Interac <noreply@interac-deposit-td.com>\nSubject: $250 e-Transfer waiting for you\n\nSarah Johnson has sent you $250.00. Deposit now at: https://td-interac-secure.com/deposit",
        "TD NOTICE: An Interac e-Transfer of $750.00 is waiting. Click to accept before it expires: http://td-etransfer-alert.com/accept?t=48h",
    ],
    "EasyWeb Password Reset Phishing": [
        "From: TD EasyWeb Security <security@td-easyweb-verify.com>\nSubject: Action Required: Verify your TD EasyWeb account\n\nDear TD Customer,\n\nWe detected unusual activity on your account. Please verify your identity within 24 hours or your account will be suspended.\n\nClick here to verify: https://easyweb-td-secure.com/verify",
        "From: TD Online Banking <noreply@tdbankcanada-security.com>\nSubject: Your EasyWeb password needs to be reset\n\nFor your security we are requiring all customers to update their passwords. Click the link below to reset: https://td-password-reset.ca/update",
        "TD SECURITY NOTICE: We've detected a login attempt from an unrecognized device. Secure your account now: https://easyweb-alert.com/secure?token=abc123",
        "From: TD Bank <security@td-account-verify.net>\nSubject: Immediate action required - account suspended\n\nYour TD EasyWeb account has been temporarily suspended due to suspicious activity. Verify immediately at: https://td-verify-account.ca",
    ],
    "CRA Tax Refund TD Account SMS": [
        "CRA: You have a tax refund of $1,247.50 pending to your TD account. Confirm your banking details: https://cra-refund-td.com/deposit",
        "Canada Revenue Agency: Tax refund available for TD customers. Deposit your $892.00 refund here: http://cra-td-refund.ca/claim",
        "CRA NOTICE: Your 2024 tax refund of $2,103.00 is ready. Link your TD account to receive: https://cra-canada-refund.com",
    ],
    "TD Visa Suspicious Activity Alert Scam": [
        "From: TD Visa Fraud Protection <fraud@td-visa-alerts.com>\nSubject: URGENT: Suspicious transaction on your TD Visa\n\nWe detected a suspicious charge of $847.32 at an unknown merchant. If this was not you, verify your card immediately: https://td-visa-verify.ca/dispute",
        "TD ALERT: Unusual activity detected on your Visa card. A purchase of $1,200 was attempted. Click to confirm or deny: https://tdvisa-fraud-alert.com/confirm",
        "From: TD Visa <security@visa-td-protection.com>\nSubject: Transaction Alert - Immediate Response Required\n\nAn international transaction of $3,421.00 was attempted on your card. Verify: https://td-secure-transactions.com",
    ],
}

LEGIT_CONTENT = [
    "From: TD Canada Trust <statements@td.com>\nSubject: Your January statement is ready\n\nYour monthly statement for your TD Every Day Checking Account ending in 4521 is now available. Log in to EasyWeb to view your statement.\n\nTD Canada Trust",
    "From: TD Canada Trust <alerts@td.com>\nSubject: New sign-in to your TD EasyWeb account\n\nWe detected a new sign-in to your TD EasyWeb account from Toronto, ON. If this was you, no action is required. If not, call 1-866-222-3456 immediately.\n\nTD Canada Trust",
    "From: TD Canada Trust <offers@td.com>\nSubject: A special offer for valued TD customers\n\nAs a valued TD customer, you may be eligible for a preferential rate on a new TD product. Visit td.com or your local TD branch to learn more. No action required.",
]

GEO_DATA = [
    ("Toronto", "ON", 43.6532, -79.3832),
    ("Mississauga", "ON", 43.5890, -79.6441),
    ("Brampton", "ON", 43.6833, -79.7667),
    ("Scarborough", "ON", 43.7764, -79.2318),
    ("North York", "ON", 43.7615, -79.4111),
    ("Hamilton", "ON", 43.2557, -79.8711),
    ("Ottawa", "ON", 45.4215, -75.6972),
    ("Montreal", "QC", 45.5017, -73.5673),
    ("Vancouver", "BC", 49.2827, -123.1207),
    ("Calgary", "AB", 51.0447, -114.0719),
]


def seed():
    init_db()
    db = SessionLocal()

    try:
        # Clear existing data
        db.query(TestEmail).delete()
        db.query(Submission).delete()
        db.query(Campaign).delete()
        db.query(User).delete()
        db.commit()

        # ── Users ──────────────────────────────────────────────────────────────
        users = [
            User(id=str(uuid.uuid4()), email="alice@example.com", name="Alice Chen",
                 reward_points=340, current_streak=3, tests_sent=9,
                 tests_flagged_correctly=7, real_submissions=4, accuracy_pct=77.8),
            User(id=str(uuid.uuid4()), email="bob@example.com", name="Bob Martinez",
                 reward_points=190, current_streak=1, tests_sent=6,
                 tests_flagged_correctly=4, real_submissions=2, accuracy_pct=66.7),
            User(id=str(uuid.uuid4()), email="carol@example.com", name="Carol Singh",
                 reward_points=510, current_streak=5, tests_sent=12,
                 tests_flagged_correctly=11, real_submissions=6, accuracy_pct=91.7),
            User(id=str(uuid.uuid4()), email="dave@example.com", name="Dave Thompson",
                 reward_points=60, current_streak=0, tests_sent=4,
                 tests_flagged_correctly=2, real_submissions=1, accuracy_pct=50.0),
            User(id=str(uuid.uuid4()), email="emma@example.com", name="Emma Osei",
                 reward_points=280, current_streak=2, tests_sent=8,
                 tests_flagged_correctly=6, real_submissions=3, accuracy_pct=75.0),
        ]
        for u in users:
            db.add(u)
        db.commit()

        # ── Campaigns ─────────────────────────────────────────────────────────
        seed_path = os.path.join(os.path.dirname(__file__), "../data/seed_campaigns.json")
        with open(os.path.abspath(seed_path)) as f:
            campaign_data = json.load(f)

        campaigns = []
        campaign_days = {}  # track days_ago per campaign id for later use
        for c in campaign_data:
            days_ago = c["first_seen_days_ago"]
            campaign = Campaign(
                id=str(uuid.uuid4()),
                label=c["label"],
                attack_vector=c["attack_vector"],
                severity=c["severity"],
                report_count=c["report_count"],
                first_seen=datetime.utcnow() - timedelta(days=days_ago),
                last_seen=datetime.utcnow() - timedelta(hours=random.randint(1, 12)),
                is_active=True,
                tactics_summary=c["tactics_summary"],
                customer_alert=c["customer_alert"],
            )
            db.add(campaign)
            campaigns.append((campaign, days_ago))
        db.commit()

        # ── Fraud Submissions ──────────────────────────────────────────────────
        submission_count = 0
        for campaign, first_seen_days_ago in campaigns:
            samples = SAMPLE_CONTENT.get(campaign.label, [])
            # Use actual report_count as guide but cap additions at 12 per campaign
            n_to_add = min(14, max(4, len(samples) * 3))

            for i in range(n_to_add):
                content = samples[i % len(samples)] if samples else f"Sample fraud content for {campaign.label}"
                geo = random.choice(GEO_DATA)
                user = random.choice(users)
                days_ago = random.randint(0, first_seen_days_ago if first_seen_days_ago else 7)

                sub = Submission(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    campaign_id=campaign.id,
                    type=campaign.attack_vector if campaign.attack_vector in ("sms", "email") else "email",
                    content=content,
                    verdict="fraud",
                    confidence=round(random.uniform(0.82, 0.98), 2),
                    city=geo[0], province=geo[1], lat=geo[2] + random.uniform(-0.05, 0.05),
                    lng=geo[3] + random.uniform(-0.05, 0.05),
                    submitted_at=datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23)),
                    is_test_email=False,
                )
                db.add(sub)
                submission_count += 1

        # ── Legit Submissions ──────────────────────────────────────────────────
        for i in range(12):
            content = LEGIT_CONTENT[i % len(LEGIT_CONTENT)]
            geo = random.choice(GEO_DATA)
            user = random.choice(users)
            sub = Submission(
                id=str(uuid.uuid4()),
                user_id=user.id,
                campaign_id=None,
                type="email",
                content=content,
                verdict="legitimate",
                confidence=round(random.uniform(0.85, 0.97), 2),
                city=geo[0], province=geo[1], lat=geo[2], lng=geo[3],
                submitted_at=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
                is_test_email=False,
            )
            db.add(sub)
            submission_count += 1

        db.commit()
        print(f"✓ Seeded {len(users)} users, {len(campaigns)} campaigns, {submission_count} submissions."  )

    finally:
        db.close()


if __name__ == "__main__":
    seed()
