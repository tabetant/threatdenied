# Threat Decoded

> Got a suspicious message claiming to be from TD? Don't wonder — ask TD. And we'll reward you for staying sharp.

TD Best AI Hack — GenAI Hackathon 2026

---

## What is this?

Threat Decoded lets TD Bank customers verify suspicious emails and texts by simply forwarding them. Instead of guessing whether a message is a scam, the customer asks TD directly — and TD actually knows, because it has ground truth on every communication it has ever sent.

On top of verification, the system trains customers by sending them fake phishing emails each month and rewarding the ones who catch them. The whole thing runs on 7 separate Claude AI agents, each handling a different job.

## Why this matters

APP fraud (authorized push payment) is the fastest-growing fraud type globally. It starts with a fake message impersonating the bank. Banks spend billions on transaction monitoring but almost nothing protects the customer *before* they get tricked.

Spam filters and antivirus tools guess based on patterns. TD can check against what it actually sent. That's the difference.

---

## How it works

### Verification

Customer gets a sketchy text or email. They forward it to `verify@td.com`. That's it — one tap, same as forwarding to a friend. No app download, no URL to visit.

The system pulls apart the forwarded message and runs five checks at the same time:

- **Sender check** — is this phone number / email / domain actually in TD's sender registry?
- **URL forensics** — where do the links actually go? How old are those domains? Are they hosted outside Canada?
- **Content analysis** — Claude reads the message looking for urgency tactics, credential requests, impersonation quality, grammar issues, threat language
- **Template matching** — does this look like how TD actually writes to customers, or is it off?
- **Campaign linking** — have other customers reported something similar? Hash the content and check

All five scores feed into a verdict engine: **FRAUD**, **LEGITIMATE**, or **INCONCLUSIVE** with a confidence percentage. The customer gets the result back with a full breakdown of what was found and why.

After a fraud verdict, customers can chat with an AI agent to ask follow-ups — "what should I do?", "should I call the police?", "did anyone else get this?"

### Training

TD sends each enrolled customer 3-10 fake phishing emails per month, mixed in with their regular email. They vary in difficulty — some are obvious, some are nearly perfect.

The customer handles them the same way they'd handle a real threat: forward to `verify@td.com`. The system knows which ones are tests.

After each one, a training coach AI explains what they caught, what they missed, and gives them tips. A scoring judge awards points for correct catches and deducts for false alarms (flagging real TD emails as fraud). This rewards accuracy over volume — you can't game it by flagging everything.

Customers track their accuracy, streaks, and TD reward points on a score card.

### Campaign intelligence

Every submission feeds into a shared intelligence layer. The campaign analyst AI clusters similar reports, names emerging campaigns (like "GTA Visa Limit Increase SMS Campaign"), and writes threat briefs.

When something new pops up, the alert writer AI drafts a customer-facing warning for TD to review and push out. The dashboard shows active campaigns, a geographic threat map, submission trends, and detection rates.

---

## The 7 AI agents

This isn't a single API call with a wrapper. Each function has its own Claude agent with a dedicated system prompt:

1. **Fraud Analyst** — scores submitted messages across five dimensions, returns a structured verdict with reasoning
2. **Phish Generator** — writes realistic test phishing emails at varying difficulty levels, plus legitimate TD emails mixed in
3. **Training Coach** — explains what the customer got right or wrong after each test, gives actionable tips, keeps it friendly
4. **Chat Agent** — conversational follow-up after a verdict, can answer "why was this flagged?" and "what do I do now?"
5. **Scoring Judge** — handles edge cases in scoring, explains point decisions when the answer isn't clear-cut
6. **Campaign Analyst** — clusters submissions, names campaigns, identifies target demographics, writes intel summaries
7. **Alert Writer** — drafts customer warnings when a new campaign is detected, ready for TD to review and send

---

## Tech stack

- **Backend:** Python 3.13, FastAPI
- **AI:** Claude (Anthropic) — Sonnet for analysis and generation, Haiku for coaching and scoring
- **Database:** SQLite + SQLAlchemy
- **Admin UI:** static HTML/CSS/JS
- **Email:** SendGrid / SMTP / simulated (configurable)

---

## Getting started

You need Python 3.10+ and an [Anthropic API key](https://console.anthropic.com/).

```bash
cd threat-decoded/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env`:

```
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=sqlite:///./threat_decoded.db
EMAIL_MODE=simulated
```

`EMAIL_MODE` controls how verdict replies are sent back to customers:

- `simulated` — prints the reply to the console (good for development, no setup needed)
- `smtp` — sends real emails through an SMTP server. Add these to your `.env`:
  ```
  SMTP_HOST=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USER=your-email@gmail.com
  SMTP_PASS=your-app-password
  SMTP_FROM=your-email@gmail.com
  ```
- `sendgrid` — sends through SendGrid. Add `SENDGRID_API_KEY=SG.xxx` to your `.env`.

To receive real forwarded emails (not just test via curl), you need an inbound email webhook. Set up SendGrid Inbound Parse or Mailgun Routes to forward incoming mail to your server's `POST /inbound` endpoint. For local development, use ngrok to expose your server (`ngrok http 8000`).

Run it:

```bash
uvicorn main:app --reload --port 8000
```

Admin dashboard at `http://localhost:8000/admin`.
