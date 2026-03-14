"""
Template matching — compares submission against known real TD communication templates.
Uses simple keyword/cosine similarity (no ML dependency needed for Phase 2).
Phase 2 implementation target.
"""
import json
import os
import re


def load_templates() -> list[dict]:
    path = os.path.join(os.path.dirname(__file__), "../../data/td_templates.json")
    with open(os.path.abspath(path)) as f:
        return json.load(f)


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"\b\w+\b", text.lower()))


def jaccard_similarity(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def check_template(content: str) -> dict:
    templates = load_templates()
    content_tokens = tokenize(content)

    best_score = 0.0
    best_match = None

    for t in templates:
        tmpl_tokens = tokenize(t.get("body_sample", "") + " " + t.get("subject_sample", ""))
        score = jaccard_similarity(content_tokens, tmpl_tokens)
        if score > best_score:
            best_score = score
            best_match = t

    if best_score > 0.35:
        return {"check": "template", "status": "pass", "title": "Template matching",
                "detail": f"Matches TD's '{best_match['name']}' template (score: {best_score:.2f}).",
                "score": best_score}
    elif best_score > 0.15:
        return {"check": "template", "status": "warning", "title": "Template matching",
                "detail": f"Partial match to TD templates (score: {best_score:.2f}). Style deviations detected.",
                "score": best_score}
    else:
        return {"check": "template", "status": "fail", "title": "Template matching",
                "detail": "Does not match any known TD communication template.",
                "score": best_score}
