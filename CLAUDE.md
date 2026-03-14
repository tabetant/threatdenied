# CLAUDE.md — Threat Decoded (TD)

## PROJECT OVERVIEW

Threat Decoded is a fraud verification tool built for the TD Best AI Hack at GenAI Hackathon. The one-line pitch:

**"Got a suspicious message claiming to be from TD? Don't wonder — ask TD. And we'll reward you for staying sharp."**

### What it does
1. **Verify**: Users forward suspicious emails/texts to TD's system. The AI runs forensic analysis (sender check, URL forensics, content AI, template matching, campaign linking) and returns a definitive verdict — not a guess, but a check against TD's own records.
2. **Incentivize**: TD sends 3-10 fake phishing test emails per month to enrolled users. Users who correctly flag all tests AND submit real phishing emails earn TD reward points. Scoring rewards accuracy, not volume — flagging legitimate TD emails as fraud loses points.
3. **Dashboard**: TD's admin view shows campaign clusters, geographic threat radar, trending fraud types, and submission volume — turning individual reports into collective intelligence.

### Tech Stack
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Framer Motion
- **Backend**: Python FastAPI, SSE streaming
- **AI (CORE)**: Claude API (Anthropic) — powers EVERYTHING, not just content analysis
- **Database**: SQLite with SQLAlchemy
- **Styling**: TD Bank brand colors (#008A4C green, #34A853, white, dark grays)

### AI-First Architecture — CRITICAL
Generative AI is not a feature of this product. It IS the product. Every major function is powered by an LLM call. Specifically:

| Function | AI Role | Details |
|----------|---------|---------|
| **Fraud analysis** | AI classifies submitted content | Forensic breakdown of why it's fraud/legit |
| **Test email generation** | AI writes the phishing test emails | Creates realistic, varied phishing scenarios targeting TD customers — different styles, attack vectors, difficulty levels each month |
| **User training & feedback** | AI explains to users what they got right/wrong | After a user flags (or misses) a test email, AI generates a personalized explanation: "Here's what you should have noticed..." |
| **Conversational interface** | AI chatbot talks with users | Users can ask follow-up questions about a verdict: "Why was this flagged?" "What should I do?" "How do I report this to police?" AI responds conversationally |
| **Scoring & validation** | AI evaluates user behavior | AI judges whether a user's flag was correct, accounts for edge cases, and explains scoring decisions |
| **Campaign intelligence** | AI clusters and labels fraud campaigns | AI analyzes patterns across submissions, names emerging campaigns, writes threat summaries for the dashboard |
| **Alert generation** | AI writes proactive customer warnings | When a new campaign is detected, AI drafts the customer-facing alert: "We're seeing a new scam targeting TD customers in Ontario..." |

Every one of these is a separate Claude API call with a task-specific system prompt. This is what makes this a genuine AI hack — not a wrapper with one API call, but an AI-native system where the model is the engine at every layer.

---

## CRITICAL RULES

### Git Identity — MANDATORY
**NEVER commit under Claude's name.** Before ANY git operation, always ensure:
```bash
git config user.name "REPLACE_WITH_MY_GITHUB_USERNAME"
git config user.email "REPLACE_WITH_MY_EMAIL"
```
Ask me for my GitHub username and email before the first commit if not already configured.

### Commit Discipline
**NEVER auto-commit. ALWAYS ask me before committing anything.** When you want to commit:
1. Show me exactly what files changed
2. Propose a commit message
3. Wait for my explicit approval
4. Only then run `git add` + `git commit`

### Agent Architecture — Credit Optimization
Use different models for different task categories to save credits:

| Task Type | Model | When to Use |
|-----------|-------|-------------|
| **Architect agent** | opus | System design, complex debugging, API design, prompt engineering for fraud analysis |
| **Backend agent** | sonnet | Python FastAPI routes, database models, analysis modules, SSE streaming |
| **Frontend agent** | sonnet | Next.js pages, React components, Tailwind styling, animations |
| **Data agent** | haiku | Seed data generation, JSON fixtures, mock data, simple scripts |
| **Test agent** | haiku | Writing tests, running linters, checking types, simple file operations |

When delegating to sub-agents, use `--model` flag to specify. Default to sonnet for most coding. Only escalate to opus for architecture decisions or hard bugs. Use haiku for anything repetitive or data-heavy.

---

## PROJECT STRUCTURE

```
threat-decoded/
├── CLAUDE.md                      # This file
├── frontend/                      # Next.js 14 App Router
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── public/
│   │   └── td-logo.svg
│   ├── app/
│   │   ├── layout.tsx             # Root layout with TD branding
│   │   ├── globals.css            # Tailwind + TD brand tokens
│   │   ├── page.tsx               # Landing: submit suspicious content
│   │   ├── scan/
│   │   │   └── [id]/page.tsx      # Live forensic analysis (SSE consumer)
│   │   ├── report/
│   │   │   └── [id]/page.tsx      # Final verdict + evidence cards
│   │   ├── profile/
│   │   │   └── page.tsx           # User score card, streak, rewards
│   │   └── dashboard/
│   │       └── page.tsx           # TD admin: campaigns, map, trends
│   └── components/
│       ├── SubmitForm.tsx          # Paste text / URL / upload screenshot
│       ├── ForensicCard.tsx        # Individual check result card
│       ├── ForensicStream.tsx      # SSE listener, renders cards as they arrive
│       ├── VerdictBanner.tsx       # FRAUD / LEGITIMATE result
│       ├── CampaignBadge.tsx       # "Part of Campaign #4721"
│       ├── ChatPanel.tsx           # AI conversational follow-up after verdict
│       ├── TrainingFeedback.tsx    # AI explains what user got right/wrong
│       ├── ScoreCard.tsx           # User accuracy + rewards display
│       ├── ThreatMap.tsx           # Geographic dot map of reports
│       ├── CampaignTable.tsx       # Dashboard campaign list
│       ├── CampaignBrief.tsx       # AI-generated threat intelligence summary
│       └── TrendChart.tsx          # Recharts submissions over time
│
├── backend/                       # Python FastAPI
│   ├── requirements.txt
│   ├── main.py                    # FastAPI app, CORS, route registration
│   ├── config.py                  # API keys, constants
│   ├── db.py                      # SQLAlchemy models + session
│   ├── models.py                  # Pydantic request/response schemas
│   ├── routes/
│   │   ├── analyze.py             # POST /api/analyze (SSE streaming)
│   │   ├── reports.py             # GET /api/report/{id}
│   │   ├── campaigns.py           # GET /api/campaigns
│   │   ├── profile.py             # GET /api/profile/{user_id}
│   │   ├── chat.py                # POST /api/chat (conversational follow-up)
│   │   ├── training.py            # GET /api/training/feedback/{submission_id}
│   │   └── dashboard.py           # GET /api/dashboard/stats
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── sender.py              # Check sender vs known TD numbers/emails
│   │   ├── url_forensics.py       # Domain age, redirect chains, WHOIS mock
│   │   ├── content_ai.py          # Claude API: fraud analysis of submitted content
│   │   ├── template_match.py      # Compare vs real TD communication templates
│   │   └── campaign.py            # Hash + cluster matching
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── client.py              # Shared Claude API client with model routing
│   │   ├── phish_generator.py     # Claude API: generate realistic test phishing emails
│   │   ├── training_coach.py      # Claude API: explain what user got right/wrong
│   │   ├── chat_agent.py          # Claude API: conversational follow-up Q&A about verdicts
│   │   ├── campaign_analyst.py    # Claude API: cluster submissions, name campaigns, write threat briefs
│   │   ├── alert_writer.py        # Claude API: draft proactive customer warnings
│   │   └── scoring_judge.py       # Claude API: evaluate edge-case user flags
│   ├── prompts/
│   │   ├── fraud_analysis.txt     # System prompt for content analysis
│   │   ├── phish_generator.txt    # System prompt for test email generation
│   │   ├── training_coach.txt     # System prompt for user feedback
│   │   ├── chat_agent.txt         # System prompt for conversational Q&A
│   │   ├── campaign_analyst.txt   # System prompt for campaign clustering
│   │   └── alert_writer.txt       # System prompt for customer alerts
│   ├── verdict.py                 # Aggregate all check scores → final decision
│   ├── seed.py                    # Script to populate DB with demo data
│   └── test_emails/               # Sample phishing + legitimate emails for testing
│       ├── phish_credit_limit.json
│       ├── phish_etransfer.json
│       ├── phish_password_reset.json
│       ├── legit_td_statement.json
│       └── legit_td_promo.json
│
└── data/
    ├── td_known_senders.json      # Real TD phone numbers, domains, email addresses
    ├── td_templates.json          # What real TD communications look like
    └── seed_campaigns.json        # Pre-seeded campaign clusters for demo
```

---

## API CONTRACTS

### POST /api/analyze
**Request:**
```json
{
  "type": "sms" | "email" | "url" | "screenshot",
  "content": "string (message body, URL, or base64 image)",
  "user_id": "string (optional, for score tracking)"
}
```
**Response:** Server-Sent Events stream. Each event:
```json
{
  "check": "sender" | "url" | "content_ai" | "template" | "campaign",
  "status": "pass" | "fail" | "warning" | "info",
  "title": "Sender verification",
  "detail": "This number is not in TD's known sender list",
  "score": 0.85,
  "metadata": {}
}
```
Final event:
```json
{
  "check": "verdict",
  "status": "fraud" | "legitimate" | "inconclusive",
  "confidence": 0.94,
  "report_id": "uuid",
  "campaign_id": "4721 or null",
  "campaign_report_count": 47
}
```

### GET /api/report/{id}
Returns the full forensic report with all check results.

### GET /api/campaigns
Returns array of active campaigns with report counts, channels, first_seen dates.

### GET /api/profile/{user_id}
Returns user's score card: tests_sent, tests_flagged_correctly, real_submissions, accuracy_pct, reward_points, current_streak.

### GET /api/dashboard/stats
Returns aggregate stats: total_submissions_today, fraud_rate, active_campaigns, top_campaign, geographic_data. Campaign labels and threat summaries are AI-generated.

### POST /api/chat
**AI-powered conversational follow-up.** User asks questions about a verdict.
**Request:**
```json
{
  "report_id": "uuid",
  "message": "Why was this flagged as fraud?",
  "history": []
}
```
**Response:**
```json
{
  "response": "Great question. This was flagged because the sender domain td-secure-verify.ca is not owned by TD Bank. TD's real domains are td.com and tdcanadatrust.com. The message also used urgency tactics — threatening account closure within 24 hours — which is a common phishing pattern TD would never use.",
  "suggested_followups": ["What should I do now?", "How do I report this?", "Has anyone else received this?"]
}
```

### GET /api/training/feedback/{submission_id}
**AI-generated training feedback** after a user flags or misses a test email.
**Response:**
```json
{
  "was_test": true,
  "user_was_correct": false,
  "ai_explanation": "This was a test email we sent you simulating a fake e-transfer notification. Here's what you should have caught: the sender address used 'td-etransfer-alert.com' instead of TD's real domain. Real Interac e-Transfers never come from TD — they come from Interac directly. Next time, always check the sender domain before clicking any link.",
  "tips": ["Always verify sender domains", "TD never sends e-transfer links — Interac does", "Look for urgency language as a red flag"],
  "difficulty": "medium"
}
```

### POST /api/training/generate-test
**AI generates a new batch of test phishing emails** for a user. Called by a scheduled job or admin trigger.
**Request:**
```json
{
  "user_id": "string",
  "count": 5,
  "difficulty": "easy" | "medium" | "hard",
  "avoid_recent_types": ["credit_limit", "password_reset"]
}
```
**Response:**
```json
{
  "test_emails": [
    {
      "id": "uuid",
      "type": "phishing",
      "subject": "Action required: verify your TD Visa",
      "body": "...",
      "from_address": "security@td-verify-account.com",
      "difficulty": "medium",
      "red_flags": ["fake domain", "urgency", "asks for credentials"]
    },
    {
      "id": "uuid", 
      "type": "legitimate",
      "subject": "Your monthly statement is ready",
      "body": "...",
      "from_address": "statements@td.com",
      "difficulty": "easy",
      "why_legitimate": ["real TD domain", "no links", "matches template"]
    }
  ]
}
```

### GET /api/campaigns/brief/{campaign_id}
**AI-generated threat intelligence brief** for the dashboard.
**Response:**
```json
{
  "campaign_id": "4721",
  "ai_summary": "This campaign impersonates TD Visa Services via SMS, targeting customers in the GTA with fake credit limit increase offers. The messages contain links to recently registered domains hosted outside Canada. First detected March 8, 2026. Velocity has increased 3x in the last 48 hours, suggesting the campaign is in active scaling phase.",
  "recommended_alert": "TD customers in Ontario: We've detected a wave of fake credit limit increase texts. TD will never text you a link to increase your credit limit. If you received this message, submit it to Threat Decoded.",
  "severity": "high"
}
```

---

## BUILD ORDER

Follow this sequence. Each phase builds on the previous.

### Phase 1: Skeleton (do this first)
1. Initialize Next.js app with TypeScript + Tailwind
2. Initialize FastAPI app with CORS configured for localhost:3000
3. Set up SQLite database with tables: submissions, campaigns, users, test_emails
4. Create the seed script with 4-5 pre-built campaigns and 50+ submissions
5. Verify both servers run and can talk to each other

### Phase 2: Backend Analysis Engine
1. Build ai/client.py — shared Claude API client with model routing (haiku for simple tasks, sonnet for analysis)
2. Build sender.py — simple JSON lookup
3. Build url_forensics.py — mock WHOIS + redirect data
4. Build content_ai.py — Claude API fraud analysis (uses prompts/fraud_analysis.txt)
5. Build template_match.py — cosine similarity against TD templates
6. Build campaign.py — hash + cluster matching
7. Build verdict.py — weighted aggregation
8. Wire up the SSE streaming endpoint in analyze.py

### Phase 3: Customer Frontend
1. Landing page with submit form (paste text, enter URL, upload)
2. Live forensic analysis page consuming SSE stream
3. Verdict/report page with evidence cards
4. ChatPanel — AI conversational follow-up after verdict (user asks questions, AI responds)
5. User profile page with score card and streak

### Phase 4: Dashboard
1. Stats bar with aggregate numbers
2. Campaign table with expand/detail
3. AI-generated campaign brief (CampaignBrief component calling /api/campaigns/brief/)
4. Geographic dot map
5. Trend chart with Recharts

### Phase 5: AI-Powered Gamification Layer
1. Build ai/phish_generator.py — Claude generates realistic test phishing emails (varied difficulty, attack vectors)
2. Build ai/training_coach.py — Claude explains what user got right/wrong after each flag
3. Build ai/scoring_judge.py — Claude evaluates edge-case flags
4. Build routes/training.py — endpoints for feedback and test generation
5. Backend: scoring logic (correct flags +points, false flags -points, real phishing submissions +bonus)
6. Frontend: TrainingFeedback component — AI explanation after flagging
7. Frontend: ScoreCard UI — streak display, reward tier, accuracy percentage

### Phase 6: AI Campaign Intelligence
1. Build ai/campaign_analyst.py — Claude clusters submissions and writes threat briefs
2. Build ai/alert_writer.py — Claude drafts customer-facing warnings
3. Wire campaign briefs into dashboard
4. Add alert preview panel to dashboard (TD admin can review AI-drafted alerts before sending)

### Phase 7: Polish
1. TD branding (green theme, clean typography)
2. Animations on forensic card reveals (Framer Motion)
3. Mobile responsiveness on customer-facing pages
4. Demo walkthrough preparation

---

## DESIGN DIRECTION

### Brand
- Primary green: #008A4C (TD's signature green)
- Dark green: #004D29
- Light green surface: #E8F5E9
- White: #FFFFFF
- Dark text: #1A1A1A
- Muted text: #6B7280
- Danger/fraud red: #DC2626
- Success/legitimate green: #16A34A
- Warning amber: #F59E0B

### Aesthetic
Clean, trustworthy, institutional — like a real banking product. No playful or startup aesthetics. Think TD's actual app UI. Generous whitespace, clear hierarchy, confident typography. The forensic analysis view is the one place to add visual flair — each check card should reveal with a smooth slide-in animation, and the verdict should land with weight.

### Typography
- Headings: font-weight 600, tracking tight
- Body: font-weight 400, relaxed line-height
- Monospace for technical details (domain names, IP addresses, hash values)

---

## AI SYSTEM PROMPTS (store each in backend/prompts/)

### fraud_analysis.txt (for content_ai.py)
```
You are a fraud analyst at TD Bank Canada. Your job is to analyze a customer-submitted message and determine if it is a legitimate TD Bank communication or a fraudulent impersonation.

Analyze the following aspects and return structured JSON:
1. urgency_tactics: Does the message create artificial urgency? (score 0-1, explanation)
2. impersonation_quality: How well does it impersonate TD's real communication style? (score 0-1, explanation)  
3. suspicious_requests: Does it ask for credentials, clicks, transfers, or personal info? (score 0-1, explanation)
4. grammar_and_formatting: Professional quality vs. errors/inconsistencies? (score 0-1, explanation)
5. threat_indicators: Threats of account closure, legal action, etc.? (score 0-1, explanation)
6. overall_assessment: Your expert verdict with reasoning

Return ONLY valid JSON, no markdown, no preamble.
```

### phish_generator.txt (for phish_generator.py)
```
You are a cybersecurity red team specialist at TD Bank Canada. Your job is to generate realistic test phishing emails that TD will send to its own customers as part of a fraud awareness training program.

Generate emails that mimic real-world phishing tactics targeting banking customers. Vary the attack vectors:
- Fake e-transfer notifications
- Account verification urgency
- Credit limit increase offers  
- Suspicious activity alerts
- Prize/reward scams impersonating TD
- Password reset requests
- Tax document / CRA scams referencing TD accounts

For each email, include: subject line, sender address (use realistic but fake domains), body text, and a list of red flags the user should catch.

Also generate some LEGITIMATE TD emails mixed in (real td.com domain, matching TD's actual communication style, no suspicious links). The user must learn to distinguish real from fake.

Vary the difficulty:
- Easy: obvious misspellings, clearly fake domains, aggressive urgency
- Medium: clean grammar, plausible domains, subtle urgency
- Hard: near-perfect impersonation, sophisticated social engineering, only domain gives it away

Return ONLY valid JSON array, no markdown, no preamble.
```

### training_coach.txt (for training_coach.py)
```
You are a friendly cybersecurity coach at TD Bank Canada. A customer has just flagged (or missed) a test phishing email as part of TD's Threat Decoded training program.

Your job is to:
1. Tell them whether they were correct
2. Explain exactly what red flags were present (or why it was legitimate)
3. Give them 2-3 specific, actionable tips they can use next time
4. Be encouraging — praise correct catches, be supportive about misses

Tone: warm, clear, non-technical. Think of explaining to a parent or grandparent. Never condescending. Use concrete examples from the specific email they reviewed.

Return ONLY valid JSON with fields: was_correct, explanation, tips[], encouragement_message.
```

### chat_agent.txt (for chat_agent.py)
```
You are a TD Bank fraud protection assistant within the Threat Decoded app. A customer has just received a fraud analysis verdict on a message they submitted. They may have follow-up questions.

You have access to the full forensic report for this submission. Answer questions about:
- Why the message was flagged/cleared
- What specific indicators were found
- What the user should do next (report to Canadian Anti-Fraud Centre, delete the message, block the number, etc.)
- How to protect themselves going forward
- Whether other TD customers have reported similar messages

Rules:
- NEVER ask for personal information (account numbers, passwords, SIN)
- NEVER provide actual TD customer service (you cannot access accounts, make changes, or process anything)
- If the user seems to be in danger or has already sent money, direct them to call TD's fraud line at 1-866-222-3456 immediately
- Be concise, warm, and professional
- Suggest 2-3 natural follow-up questions the user might want to ask

Return ONLY valid JSON with fields: response, suggested_followups[].
```

### campaign_analyst.txt (for campaign_analyst.py)
```
You are a threat intelligence analyst at TD Bank Canada. You are reviewing a cluster of similar fraud submissions reported by TD customers through Threat Decoded.

Given a set of submissions with similar content hashes, your job is to:
1. Name the campaign with a descriptive label (e.g., "GTA Visa limit increase SMS campaign")
2. Identify the attack vector (SMS, email, phone, etc.)
3. Summarize the tactics used
4. Assess severity (low/medium/high/critical) based on sophistication and volume
5. Write a customer-facing alert that TD could push to all enrolled users
6. Estimate the target demographic if patterns are visible

Return ONLY valid JSON with fields: campaign_label, attack_vector, tactics_summary, severity, customer_alert, target_demographic, recommended_actions[].
```

### alert_writer.txt (for alert_writer.py)
```
You are a communications specialist at TD Bank Canada. A new fraud campaign has been detected through Threat Decoded.

Write a clear, concise customer-facing alert that TD can push to all enrolled customers. The alert should:
- Be under 3 sentences
- Describe what the scam looks like (without reproducing it exactly)
- Tell customers what to do if they received it
- Reinforce that TD will never ask for X, Y, Z via this channel

Tone: authoritative but not alarming. Factual. Trustworthy.

Return ONLY the alert text as a plain string, no JSON, no markdown.
```

---

## DEMO SCENARIOS (for testing + video)

### Scenario 1: Fake TD credit limit increase SMS
```
TD Alert: Congratulations! Your TD Visa credit limit has been pre-approved for an increase to $15,000. Verify your identity to activate: https://td-secure-verify.ca/activate
```
Expected: FRAUD. URL is not a TD domain. TD doesn't send credit limit increases via SMS with links.

### Scenario 2: Fake TD e-transfer notification
```
From: TD Canada Trust <notifications@td-etransfer-alert.com>
Subject: You've received an Interac e-Transfer

You've received $500.00 from John Smith. 
To deposit your money, click here: https://td-etransfer-alert.com/deposit
This transfer will expire in 24 hours.
```
Expected: FRAUD. Domain is not td.com. Real e-transfers come from Interac, not TD.

### Scenario 3: Legitimate TD statement notification
```
From: TD Canada Trust <statements@td.com>
Subject: Your January statement is ready

Your monthly statement for your TD Every Day Checking Account ending in 4521 is now available. Log in to EasyWeb to view your statement.

TD Canada Trust
```
Expected: LEGITIMATE. Correct domain. No links. Matches TD's real template style.

---

## AI CLIENT ARCHITECTURE (for ai/client.py)

Create a shared client that routes to different model tiers based on task complexity:

```python
# ai/client.py — shared Claude API wrapper with model routing
import anthropic

client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

# Model routing: save credits by using the right model for each task
MODELS = {
    "analysis": "claude-sonnet-4-20250514",      # Fraud analysis, content AI
    "generation": "claude-sonnet-4-20250514",     # Test email generation, alerts
    "chat": "claude-sonnet-4-20250514",           # Conversational follow-up
    "coaching": "claude-haiku-4-5-20251001",      # Training feedback (simpler task)
    "scoring": "claude-haiku-4-5-20251001",       # Flag evaluation (simpler task)
    "clustering": "claude-sonnet-4-20250514",     # Campaign analysis
}

def call_ai(task_type: str, system_prompt: str, user_message: str, max_tokens: int = 1024) -> str:
    model = MODELS.get(task_type, "claude-sonnet-4-20250514")
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text
```

Load system prompts from the `prompts/` directory. Never hardcode prompts inline — keep them in .txt files so they can be iterated on without touching code.

---

## REMINDER
- NEVER commit without asking me first
- NEVER use Claude's name in git config
- Use haiku for simple AI tasks (coaching, scoring), sonnet for analysis/generation
- AI powers EVERYTHING — analysis, test generation, training, chat, campaigns, alerts
- Every major feature should have its own system prompt in prompts/
- Keep the demo flow in mind: submit → live analysis → verdict → chat follow-up → dashboard
- The pitch is simple: "Your bank shouldn't guess. It should know."
- Count of distinct AI-powered features for judges: 7 (analysis, test generation, training coach, chat agent, scoring judge, campaign analyst, alert writer)
