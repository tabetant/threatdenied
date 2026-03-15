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

    # Strip forwarding metadata from the body so the AI only analyzes
    # the original email content, not the "From:" / "Subject:" headers
    # that get prepended when someone forwards an email.
    original_body = strip_forwarding_headers(text_body or html_body or "")

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


def strip_forwarding_headers(body: str) -> str:
    """Remove forwarding 'From:' and 'Subject:' lines from the top of the body.

    When a user forwards an email, the body often starts with lines like:
        From: TD Canada Trust <statements@td.com>
        Subject: Your statement is ready

    These confuse the AI because the 'From' in the body conflicts with the
    actual sender metadata. Strip them so the AI only sees the message content.
    """
    lines = body.split('\n')
    start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Skip lines that look like forwarding headers
        if re.match(r'^(From|Subject|Date|To|Sent|Cc):\s', stripped, re.IGNORECASE):
            start = i + 1
            continue
        # Skip blank lines between headers and body
        if stripped == '' and start > 0 and i == start:
            start = i + 1
            continue
        # Once we hit a non-header, non-blank line, stop
        break

    result = '\n'.join(lines[start:]).strip()
    # If stripping removed everything, return original
    return result if result else body.strip()
