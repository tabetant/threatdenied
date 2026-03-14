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
            User(id="demo-user-1", email="alice@example.com", name="Alice Chen",
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

        # ── TestEmails for demo-user-1 ─────────────────────────────────────────
        demo_user_id = "demo-user-1"
        test_emails = [
            # 1. Phishing (easy) — flagged correctly as phishing
            TestEmail(
                id=str(uuid.uuid4()),
                user_id=demo_user_id,
                type="phishing",
                subject="Action Required: Reset Your TD EasyWeb Password Now",
                body=(
                    "Dear TD Customer,\n\n"
                    "We have detected suspisious activityy on your account. "
                    "Your TD EasyWeb password must be reset immediatly or your account will be SUSPENDED.\n\n"
                    "Click here to reset NOW: https://td-reset-account.com/secure?token=839fj2\n\n"
                    "Failure to comply within 24 hours will result in account closure.\n\n"
                    "TD Security Team"
                ),
                from_address="security@td-reset-account.com",
                difficulty="easy",
                was_flagged=True,
                flagged_at=datetime.utcnow() - timedelta(days=5),
                red_flags=json.dumps(["fake domain td-reset-account.com", "spelling errors", "urgency threat", "asks to click link"]),
                why_legitimate=None,
                sent_at=datetime.utcnow() - timedelta(days=6),
            ),
            # 2. Phishing (medium) — flagged correctly as phishing
            TestEmail(
                id=str(uuid.uuid4()),
                user_id=demo_user_id,
                type="phishing",
                subject="You have received an Interac e-Transfer of $350.00",
                body=(
                    "Hello,\n\n"
                    "Mark Wilson has sent you $350.00 via Interac e-Transfer.\n\n"
                    "To deposit your funds, please click the secure link below:\n"
                    "https://td-etransfer-verify.ca/deposit?ref=TDE84729\n\n"
                    "This transfer will expire in 24 hours. Do not share this link.\n\n"
                    "TD Canada Trust"
                ),
                from_address="alerts@td-etransfer-verify.ca",
                difficulty="medium",
                was_flagged=True,
                flagged_at=datetime.utcnow() - timedelta(days=3),
                red_flags=json.dumps(["fake domain td-etransfer-verify.ca", "real e-transfers come from Interac not TD", "link to non-td domain"]),
                why_legitimate=None,
                sent_at=datetime.utcnow() - timedelta(days=4),
            ),
            # 3. Phishing (hard) — missed (user said legitimate)
            TestEmail(
                id=str(uuid.uuid4()),
                user_id=demo_user_id,
                type="phishing",
                subject="Please verify your TD account information",
                body=(
                    "Dear Valued TD Customer,\n\n"
                    "As part of our ongoing commitment to security, we periodically ask customers "
                    "to verify their account information. This is a routine process.\n\n"
                    "Please take a moment to confirm your details are up to date:\n"
                    "https://td-customerservice.ca/verify-account\n\n"
                    "If you have any questions, please contact us at 1-866-222-3456.\n\n"
                    "Thank you for banking with TD.\n\n"
                    "TD Canada Trust Customer Service"
                ),
                from_address="noreply@td-customerservice.ca",
                difficulty="hard",
                was_flagged=False,
                flagged_at=datetime.utcnow() - timedelta(days=2),
                red_flags=json.dumps(["domain is td-customerservice.ca not td.com", "TD never asks for account verification by email link"]),
                why_legitimate=None,
                sent_at=datetime.utcnow() - timedelta(days=3),
            ),
            # 4. Legitimate (easy) — flagged correctly as legitimate
            TestEmail(
                id=str(uuid.uuid4()),
                user_id=demo_user_id,
                type="legitimate",
                subject="Your February statement is ready",
                body=(
                    "Your monthly statement for your TD Every Day Checking Account ending in 4521 "
                    "is now available. Log in to EasyWeb at easyweb.td.com to view your statement.\n\n"
                    "TD Canada Trust"
                ),
                from_address="statements@td.com",
                difficulty="easy",
                was_flagged=False,
                flagged_at=datetime.utcnow() - timedelta(days=10),
                red_flags=None,
                why_legitimate=json.dumps(["real TD domain statements@td.com", "no suspicious links", "matches TD statement template", "no urgency"]),
                sent_at=datetime.utcnow() - timedelta(days=11),
            ),
            # 5. Legitimate (medium) — incorrectly flagged as phishing
            TestEmail(
                id=str(uuid.uuid4()),
                user_id=demo_user_id,
                type="legitimate",
                subject="Exclusive offer: 3% cashback on all purchases this weekend",
                body=(
                    "Hi Alice,\n\n"
                    "As a valued TD Visa cardholder, we're pleased to offer you 3% cashback "
                    "on all purchases made this weekend (March 14-15).\n\n"
                    "No action required — the offer is automatically applied to your card ending in 4521.\n\n"
                    "Visit td.com/rewards to learn more about TD rewards.\n\n"
                    "TD Canada Trust"
                ),
                from_address="offers@td.com",
                difficulty="medium",
                was_flagged=True,
                flagged_at=datetime.utcnow() - timedelta(days=1),
                red_flags=None,
                why_legitimate=json.dumps(["real TD domain offers@td.com", "no links to click", "directs to td.com not a third-party site", "no credentials requested"]),
                sent_at=datetime.utcnow() - timedelta(days=2),
            ),
            # 6. Phishing (medium) — pending (not yet flagged)
            TestEmail(
                id=str(uuid.uuid4()),
                user_id=demo_user_id,
                type="phishing",
                subject="ALERT: Suspicious transaction detected on your TD account",
                body=(
                    "TD Fraud Protection has detected unusual activity on your account.\n\n"
                    "A purchase of $1,247.00 was attempted at an unknown international merchant. "
                    "If this was not you, you must verify your identity immediately to prevent further charges.\n\n"
                    "Secure your account now: https://td-fraud-protection.ca/verify?case=FR-29847\n\n"
                    "You have 2 hours to respond before your card is permanently blocked.\n\n"
                    "TD Fraud Protection Team"
                ),
                from_address="fraud-alerts@td-fraud-protection.ca",
                difficulty="medium",
                was_flagged=None,
                flagged_at=None,
                red_flags=json.dumps(["fake domain td-fraud-protection.ca", "extreme urgency (2-hour deadline)", "threatens permanent account block", "link to non-td domain"]),
                why_legitimate=None,
                sent_at=datetime.utcnow() - timedelta(hours=2),
            ),
        ]
        for te in test_emails:
            db.add(te)
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
        print(f"✓ Seeded {len(users)} users, {len(campaigns)} campaigns, {submission_count} submissions, {len(test_emails)} test emails.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
