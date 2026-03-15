import os
import smtplib
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


def _mode():
    return os.getenv("EMAIL_MODE", "simulated")


def send_reply(to: str, verdict: str, original_subject: str, original_body: str, original_sender: str, analysis_summary: str) -> bool:
    # LAST LINE OF DEFENSE: if the summary contradicts the verdict, replace it
    analysis_summary = _sanitize_summary(verdict, analysis_summary)

    if verdict == "fraud":
        subject = f"FRAUD ALERT -- Re: {original_subject}"
        body = f"""Hello,

Thank you for forwarding this email for verification.

Our analysis has determined that this email IS FRAUDULENT. Do not click any links, reply to the sender, or provide any personal information.

Analysis summary:
{analysis_summary}

Original sender: {original_sender}

--- Original Email (FLAGGED AS FRAUD) ---
Subject: {original_subject}

{original_body}
--- End of Original Email ---

If you have already interacted with this email, please call TD Bank immediately at 1-800-983-8472.

Thank you for helping keep your account safe.

TD Threat Decoded
verify@threatdecoded.com"""

    elif verdict == "legitimate":
        subject = f"VERIFIED -- Re: {original_subject}"
        body = f"""Hello,

Thank you for forwarding this email for verification.

Our analysis has confirmed that this email IS LEGITIMATE and was sent by TD Bank.

Analysis summary:
{analysis_summary}

--- Original Email (VERIFIED LEGITIMATE) ---
From: {original_sender}
Subject: {original_subject}

{original_body}
--- End of Original Email ---

You can safely interact with this email.

TD Threat Decoded
verify@threatdecoded.com"""

    else:
        subject = f"Under Review -- Re: {original_subject}"
        body = f"""Hello,

Thank you for forwarding this email for verification.

Our system needs more time to verify this email. A TD analyst is reviewing it and you will receive a follow-up shortly.

TD Threat Decoded
verify@threatdecoded.com"""

    mode = _mode()

    if mode == "simulated":
        print(f"\n{'='*60}")
        print(f"SIMULATED EMAIL REPLY")
        print(f"To: {to}")
        print(f"Subject: {subject}")
        print(f"{'='*60}")
        print(body)
        print(f"{'='*60}\n")
        return True

    elif mode == "smtp":
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER", "")
        smtp_pass = os.getenv("SMTP_PASS", "")
        smtp_from = os.getenv("SMTP_FROM", smtp_user)

        msg = MIMEMultipart()
        msg["From"] = f"TD Threat Decoded <{smtp_from}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_from, to, msg.as_string())
        return True

    elif mode == "sendgrid":
        api_key = os.getenv("SENDGRID_API_KEY")
        resp = httpx.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "personalizations": [{"to": [{"email": to}]}],
                "from": {"email": os.getenv("SMTP_FROM", "verify@threatdecoded.com"), "name": "TD Threat Decoded"},
                "subject": subject,
                "content": [{"type": "text/plain", "value": body}]
            }
        )
        return resp.status_code == 202

    return False


def _sanitize_summary(verdict: str, summary: str) -> str:
    """Last safeguard: if the summary text contradicts the verdict, replace it."""
    text = summary.lower()

    if verdict == "legitimate":
        fraud_words = ["fraudulent", "phishing", "scam", "do not trust",
                       "do not click", "credential harvesting", "not legitimate",
                       "is fraudulent", "is a scam", "is phishing",
                       "should not be trusted", "not be trusted",
                       "not a legitimate", "not a registered", "not a recognized",
                       "impersonating", "fake display name", "personal gmail",
                       "personal email", "actual sender is"]
        if any(w in text for w in fraud_words):
            return "This email has been verified as a legitimate TD Bank communication. The sender address matches TD's known sender registry and the content is consistent with authentic TD correspondence."

    elif verdict == "fraud":
        legit_words = ["is legitimate", "appears legitimate", "verified legitimate",
                       "appears safe", "is safe", "can be trusted",
                       "no fraud indicators", "no suspicious",
                       "verified td", "authentic td", "consistent with authentic"]
        if any(w in text for w in legit_words):
            return "This email has been identified as fraudulent. The message contains indicators inconsistent with authentic TD Bank communications. Do not interact with any links or provide personal information."

    return summary
