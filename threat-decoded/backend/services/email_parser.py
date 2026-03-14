import re


def parse_inbound_email(form_data) -> dict:
    raw_from = form_data.get("from", "")
    subject = form_data.get("subject", "")
    text_body = form_data.get("text", "")
    html_body = form_data.get("html", "")
    headers = form_data.get("headers", "")

    forwarded_by = extract_email_address(raw_from)
    original_sender = extract_original_sender(text_body)
    original_subject = re.sub(r'^(Fwd?|FW|Fw):\s*', '', subject, flags=re.IGNORECASE).strip()
    original_body = text_body or html_body or ""

    return {
        "forwarded_by": forwarded_by,
        "original_sender": original_sender,
        "original_subject": original_subject,
        "original_body": original_body,
        "original_headers": headers,
        "raw_email": f"From: {raw_from}\nSubject: {subject}\n\n{original_body}"
    }


def extract_email_address(from_field: str) -> str:
    match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', from_field)
    return match.group(0) if match else from_field


def extract_original_sender(body: str) -> str:
    patterns = [
        r'From:\s*.*?<([\w.+-]+@[\w.-]+\.\w+)>',
        r'From:\s*([\w.+-]+@[\w.-]+\.\w+)',
        r'from:\s*.*?<([\w.+-]+@[\w.-]+\.\w+)>',
        r'from:\s*([\w.+-]+@[\w.-]+\.\w+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, body, re.IGNORECASE)
        if match:
            return match.group(1)
    return "unknown"
