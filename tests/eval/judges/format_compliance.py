# Copyright 2026 Google LLC
import re


def evaluate(instance: dict) -> dict:
    """Programmatic metric: evaluates schedule markdown formatting."""
    text = instance.get("response", "")
    if isinstance(text, dict):
        text = str(text)

    has_headers = bool(re.search(r"###\s*Day\s*\d+", text, re.IGNORECASE))
    has_times = bool(
        re.search(
            r"\d{1,2}:\d{2}\s*(AM|PM)?\s*[-]\s*\d{1,2}:\d{2}", text, re.IGNORECASE
        )
    )
    has_transit = bool(
        re.search(r"(transit|travel|walk|drive|min)", text, re.IGNORECASE)
    )
    has_checklist = bool(re.search(r"-\s*\[\s*\]", text))

    score = (
        (0.3 * has_headers)
        + (0.3 * has_times)
        + (0.2 * has_transit)
        + (0.2 * has_checklist)
    )
    return {
        "score": round(score, 2),
        "explanation": f"Headers={has_headers}, Times={has_times}, Transit={has_transit}, Checklist={has_checklist}",
    }
