"""
URL forensics — domain age, redirect chain analysis, WHOIS (mocked for demo).
Phase 2 implementation target.
"""
import re
from datetime import datetime, timedelta
import random


SUSPICIOUS_TLDS = {".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".click", ".loan"}
TD_DOMAINS = {"td.com", "tdcanadatrust.com", "tdbank.com", "tdinsurance.com", "tdwaterhouse.ca"}


def extract_urls(content: str) -> list[str]:
    return re.findall(r"https?://[^\s\"\'>]+", content)


def mock_whois(domain: str) -> dict:
    """Mock WHOIS data — Phase 2 can integrate a real WHOIS API."""
    if domain in TD_DOMAINS:
        return {"registered": "1995-03-15", "registrar": "CSC Corporate Domains", "country": "CA"}
    seed = sum(ord(c) for c in domain)
    days_old = (seed % 400) + 1
    reg_date = (datetime.utcnow() - timedelta(days=days_old)).strftime("%Y-%m-%d")
    return {"registered": reg_date, "registrar": "NameCheap", "country": "US", "days_old": days_old}


def check_urls(content: str) -> dict:
    urls = extract_urls(content)
    if not urls:
        return {"check": "url", "status": "info", "title": "URL forensics",
                "detail": "No URLs found in submission.", "score": None}

    flags = []
    worst_score = 1.0

    for url in urls:
        domain = re.sub(r"https?://", "", url).split("/")[0].lower()
        base_domain = ".".join(domain.split(".")[-2:])

        if base_domain in TD_DOMAINS:
            continue

        whois = mock_whois(base_domain)
        days_old = whois.get("days_old", 9999)

        tld = "." + domain.split(".")[-1]
        if tld in SUSPICIOUS_TLDS:
            flags.append(f"{domain}: suspicious TLD '{tld}'")
            worst_score = min(worst_score, 0.05)
        elif days_old < 30:
            flags.append(f"{domain}: registered only {days_old} days ago")
            worst_score = min(worst_score, 0.1)
        elif days_old < 180:
            flags.append(f"{domain}: recently registered ({days_old} days ago)")
            worst_score = min(worst_score, 0.4)
        else:
            flags.append(f"{domain}: not a TD domain")
            worst_score = min(worst_score, 0.5)

    if not flags:
        return {"check": "url", "status": "pass", "title": "URL forensics",
                "detail": "All URLs point to verified TD domains.", "score": 1.0}

    status = "fail" if worst_score < 0.2 else "warning"
    return {
        "check": "url", "status": status, "title": "URL forensics",
        "detail": "; ".join(flags), "score": worst_score,
        "metadata": {"urls_found": urls},
    }
