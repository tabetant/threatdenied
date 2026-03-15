import re


def parse_inbound_email(form_data) -> dict:
    raw_from = form_data.get("from", "")
    subject = form_data.get("subject", "")
    text_body = form_data.get("text", "")
    html_body = form_data.get("html", "")
    headers = form_data.get("headers", "")

    forwarded_by = extract_email_address(raw_from)
    original_sender = extract_original_sender(text_body, forwarded_by)
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


def extract_original_sender(body: str, forwarded_by: str = "") -> str:
    """
    Gmail forward format:
      ---------- Forwarded message ---------
      From: Suspicious Sender <bad@td-banking.com>
      ...
    We look for the FIRST "From:" that comes AFTER the forwarded message divider
    and is NOT the forwarder's own address.
    """
    # Try to isolate the forwarded block first
    divider = re.search(
        r'-{3,}\s*Forwarded message\s*-{3,}|Begin forwarded message|Original Message',
        body, re.IGNORECASE
    )
    search_body = body[divider.end():] if divider else body

    patterns = [
        r'From:\s*.*?<([\w.+-]+@[\w.-]+\.\w+)>',
        r'From:\s*([\w.+-]+@[\w.-]+\.\w+)',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, search_body, re.IGNORECASE):
            addr = match.group(1)
            # Skip if it matches the forwarder's address
            if forwarded_by and addr.lower() == forwarded_by.lower():
                continue
            return addr

    return "unknown"
