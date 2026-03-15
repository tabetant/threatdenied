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

    # Strip ALL forwarding metadata from the body so Claude only sees
    # the original email content — not Gmail forwarding headers, not
    # the forwarder's email address, nothing that could confuse the AI.
    original_body = strip_forwarding_metadata(text_body or html_body or "", forwarded_by)

    return {
        "forwarded_by": forwarded_by,
        "original_sender": original_sender,
        "original_subject": original_subject,
        "original_body": original_body,
        "original_headers": headers,
        "raw_email": f"From: {raw_from}\nSubject: {subject}\n\n{text_body}"
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


def strip_forwarding_metadata(body: str, forwarded_by: str = "") -> str:
    """Remove all forwarding metadata from the email body.

    Handles multiple forwarding formats:
    - Gmail: "---------- Forwarded message ---------" block
    - Outlook: "From: ... Sent: ... To: ... Subject: ..."
    - Generic: "From:" / "Subject:" lines at the top
    - Quoted text with ">" prefixes

    Also removes any mention of the forwarder's email address so Claude
    cannot confuse the forwarder with the original sender.
    """
    # Step 1: Remove Gmail forwarding block
    # "---------- Forwarded message ---------\nFrom: ...\nDate: ...\nSubject: ...\nTo: ...\n"
    body = re.sub(
        r'-{5,}\s*Forwarded message\s*-{5,}\s*\n'
        r'(?:(?:From|Date|Subject|To|Cc|Bcc|Sent):.*\n)*'
        r'\n*',
        '', body, flags=re.IGNORECASE
    )

    # Step 2: Remove Outlook-style forwarding block
    # "From: Someone\nSent: ...\nTo: ...\nSubject: ..."
    body = re.sub(
        r'^From:\s.*\nSent:\s.*\nTo:\s.*\nSubject:\s.*\n\n*',
        '', body, flags=re.IGNORECASE | re.MULTILINE
    )

    # Step 3: Strip header-like lines from the very top of the body
    lines = body.split('\n')
    start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r'^(From|Subject|Date|To|Sent|Cc|Bcc):\s', stripped, re.IGNORECASE):
            start = i + 1
            continue
        if stripped == '' and start > 0 and i == start:
            start = i + 1
            continue
        break
    body = '\n'.join(lines[start:])

    # Step 4: Remove the forwarder's email address from the body entirely
    # This prevents Claude from seeing "carlgergi6@gmail.com" anywhere in the text
    if forwarded_by and '@' in forwarded_by:
        body = body.replace(forwarded_by, '[customer]')

    # Step 5: Remove any ">" quoted-text prefixes
    body = re.sub(r'^>\s?', '', body, flags=re.MULTILINE)

    result = body.strip()
    return result if result else (body.strip() or "(empty)")
