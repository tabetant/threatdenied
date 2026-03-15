<p align="center">
  <img src="https://img.shields.io/badge/TD-Threat_Denied-008A4C?style=for-the-badge&labelColor=004D29" alt="Threat Denied"/>
</p>

<h1 align="center">🛡️ Threat Denied</h1>

<p align="center">
  <strong>Your bank shouldn't guess. It should know.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Claude_AI-Anthropic-6B4FBB?logo=anthropic&logoColor=white" alt="Claude"/>
  <img src="https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white" alt="SQLite"/>
  <img src="https://img.shields.io/badge/GenAI_Genesis-Hackathon_2026-008A4C" alt="Hackathon"/>
</p>

<p align="center">
  Forward suspicious emails to <code>verify@td.com</code>. AI checks if TD actually sent it. Get rewarded for catching fraud.
</p>

---

## 🎯 The Problem

Banks catch 95% of fraud. But that last 5% still lands in the customer's inbox — and they have no way to know if it's real.

Spam filters **guess** based on patterns. TD has something no third party has: **ground truth**. TD knows exactly what it sent, to whom, and when. The system was never the problem. The user was unprotected.

> APP fraud (authorized push payment) is the fastest-growing fraud type globally. It always starts with a fake message impersonating the bank — before any transaction ever happens.

---

## 💡 The Solution

**One action. One answer. No guessing.**

A customer gets a sketchy text or email. They forward it to `verify@td.com`. That's it — one tap, same as forwarding to a friend. No app download, no URL to visit, no content to paste.

The AI doesn't guess. It checks TD's own records and delivers a **definitive verdict** with full evidence.

---

## ⚙️ How It Works

### 1. Verification

The system ingests the forwarded email — headers, sender info, links, body — and runs **five forensic checks in parallel**:

| Check | What it does |
|-------|-------------|
| **Sender verification** | Is this phone number / email / domain in TD's known sender registry? |
| **URL forensics** | Where do the links actually go? How old are those domains? Hosted outside Canada? |
| **Content analysis** | Claude reads the message for urgency tactics, credential requests, impersonation quality, grammar |
| **Template matching** | Does this match how TD actually writes to customers, or is it off? |
| **Campaign linking** | Have other customers reported something similar? Hash the content and check |

All five scores feed into the **Verdict Engine** → `FRAUD` / `LEGITIMATE` / `INCONCLUSIVE` with a confidence percentage. The customer gets the result back with a full breakdown of what was found and why.

After a fraud verdict, customers can chat with an AI agent for follow-ups — *"What should I do?" "Should I call the police?" "Did anyone else get this?"*

### 2. Training & Gamification

TD sends each enrolled customer **3–10 fake phishing emails per month**, mixed into their regular inbox. Difficulty varies — some are obvious, some are near-perfect.

Customers handle them the same way: forward to `verify@td.com`. The system knows which ones are tests.

| What happens | How it works |
|-------------|-------------|
| ✅ Correctly flag a test | Earn TD reward points |
| ✅ Submit a real phishing email | Bonus points if it matches a campaign |
| ❌ Miss a test | AI coach explains what you should have caught |
| ❌ Flag a real TD email as fraud | Lose points — accuracy matters, not volume |

After each flag, the **AI Training Coach** gives personalized feedback: what they caught, what they missed, and tips for next time. Customers track accuracy, streaks, and rewards on their score card.

### 3. Campaign Intelligence

Every submission feeds into a shared intelligence layer:
```
Individual reports → AI clusters similar submissions → Named campaigns emerge
                                                        ↓
                              TD Dashboard ← AI writes threat briefs + customer alerts
                                                        ↓
                              TD pushes proactive warnings to all customers
```

The dashboard shows active campaigns, a geographic threat map, submission trends, and detection rates — all powered by AI-generated analysis.

---

## 🤖 The 7 AI Agents

This isn't a single API call with a wrapper. **Every major function runs on its own Claude agent** with a dedicated system prompt:

| # | Agent | Role |
|---|-------|------|
| 1 | **Fraud Analyst** | Scores submitted messages across five dimensions, returns a structured verdict with reasoning |
| 2 | **Phish Generator** | Writes realistic test phishing emails at varying difficulty, plus legitimate TD emails mixed in |
| 3 | **Training Coach** | Explains what the customer got right or wrong, gives actionable tips, keeps it friendly |
| 4 | **Chat Agent** | Conversational follow-up after a verdict — answers "why?" and "what now?" |
| 5 | **Scoring Judge** | Handles edge cases in scoring, explains point decisions when the answer isn't clear-cut |
| 6 | **Campaign Analyst** | Clusters submissions, names campaigns, identifies target demographics, writes intel summaries |
| 7 | **Alert Writer** | Drafts customer warnings when a new campaign is detected, ready for TD to review and send |

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.13, FastAPI, SSE streaming |
| AI | Claude (Anthropic) — Sonnet for analysis/generation, Haiku for coaching/scoring |
| Database | SQLite + SQLAlchemy |
| Admin UI | Static HTML / CSS / JS |
| Email | SendGrid / SMTP / simulated (configurable) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- [Anthropic API key](https://console.anthropic.com/)

### Install
```bash
cd threat-denied/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure

Create `backend/.env`:
```env
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=sqlite:///./threat_denied.db
EMAIL_MODE=simulated
```

#### Email modes

| Mode | Description | Extra config needed |
|------|------------|-------------------|
| `simulated` | Prints verdict replies to console. Best for development. | None |
| `smtp` | Sends real emails via SMTP. | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM` |
| `sendgrid` | Sends via SendGrid API. | `SENDGRID_API_KEY` |

#### Receiving real forwarded emails

To accept real forwarded emails (not just test via curl), set up an inbound email webhook:
- **SendGrid Inbound Parse** or **Mailgun Routes** → forward to your server's `POST /inbound` endpoint
- For local development: `ngrok http 8000` to expose your server

### Run
```bash
uvicorn main:app --reload --port 8000
```

Admin dashboard → [`http://localhost:8000/admin`](http://localhost:8000/admin)

---

## 📁 Project Structure
```
threat-denied/
├── backend/
│   ├── main.py                 # FastAPI app entry
│   ├── email_ingestion.py      # Parses forwarded emails
│   ├── db.py                   # SQLAlchemy models
│   ├── models.py               # Pydantic schemas
│   ├── verdict.py              # Weighted score aggregation
│   ├── seed.py                 # Demo data population
│   ├── routes/
│   │   ├── analyze.py          # POST /api/analyze (SSE)
│   │   ├── chat.py             # POST /api/chat
│   │   ├── training.py         # Training feedback + test generation
│   │   ├── campaigns.py        # Campaign endpoints
│   │   ├── profile.py          # User score card
│   │   └── dashboard.py        # Admin stats
│   ├── analyzers/
│   │   ├── sender.py           # Known sender lookup
│   │   ├── url_forensics.py    # Domain age, redirects
│   │   ├── content_ai.py       # Claude fraud analysis
│   │   ├── template_match.py   # Compare vs real TD templates
│   │   └── campaign.py         # Content hash + clustering
│   ├── ai/
│   │   ├── client.py           # Shared Claude client + model routing
│   │   ├── phish_generator.py  # Test email generation
│   │   ├── training_coach.py   # User feedback
│   │   ├── chat_agent.py       # Conversational Q&A
│   │   ├── scoring_judge.py    # Edge-case evaluation
│   │   ├── campaign_analyst.py # Cluster + name campaigns
│   │   └── alert_writer.py     # Draft customer warnings
│   └── prompts/                # System prompts (one .txt per agent)
├── admin/                      # Static dashboard UI
└── data/
    ├── td_known_senders.json
    ├── td_templates.json
    └── seed_campaigns.json
```

---

<p align="center">
  <strong>Threat Denied</strong> — because TD shouldn't guess. They should know.
</p>
