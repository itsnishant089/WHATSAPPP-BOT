from __future__ import annotations

import re

from app.models.message_models import UserPreferences
from app.utils.text import tokenize

BRANCH_ALIASES = {
    "cse": "CSE",
    "computer": "CSE",
    "computer engineering": "CSE",
    "mech": "Mechanical",
    "mechanical": "Mechanical",
    "civil": "Civil",
    "electrical": "Electrical",
    "ece": "ECE",
    "electronics": "ECE",
    "ai": "AI & ML",
    "aiml": "AI & ML",
    "automobile": "Automobile",
    "chemical": "Chemical",
}

EXAM_ALIASES = {
    "leet": "HSBTE LEET",
    "ocet": "HSBTE LEET",
    "haryana leet": "HSBTE LEET",
    "diploma": "HSBTE Diploma",
    "hsbte": "HSBTE",
}


def extract_preference_updates(text: str, current: UserPreferences | None, user_id: str) -> UserPreferences:
    prefs = current or UserPreferences(whatsapp_user_id=user_id)
    lowered = text.lower()
    tokens = tokenize(text)

    if re.search(r"\b(branch|mera branch|i am|i'm|student)\b", lowered) or "branch" in lowered:
        for alias, canonical in BRANCH_ALIASES.items():
            if alias in lowered:
                prefs.branch = canonical
                break
    else:
        for alias, canonical in BRANCH_ALIASES.items():
            if alias in tokens or alias in lowered:
                if prefs.branch is None and any(w in lowered for w in ("branch", "student", "mera", "mera")):
                    prefs.branch = canonical

    for alias, canonical in BRANCH_ALIASES.items():
        if re.search(rf"\b(my branch is|branch is|branch:)\s*{re.escape(alias)}", lowered):
            prefs.branch = canonical

    if "hindi" in lowered:
        prefs.language = "hi"
    elif "english" in lowered and "hindi" not in lowered:
        prefs.language = "en"

    for alias, canonical in EXAM_ALIASES.items():
        if alias in lowered and ("exam" in lowered or "leet" in lowered or "prepare" in lowered):
            prefs.target_exam = canonical

    if "haryana" in lowered:
        prefs.state = "Haryana"

    prefs.whatsapp_user_id = user_id
    return prefs


def infer_search_hints(text: str, prefs: UserPreferences | None) -> tuple[str | None, str | None]:
    lowered = text.lower()
    branch = prefs.branch if prefs else None
    exam = prefs.target_exam if prefs else None
    for alias, canonical in BRANCH_ALIASES.items():
        if alias in lowered:
            branch = canonical
            break
    if "leet" in lowered or "ocet" in lowered:
        exam = "HSBTE LEET"
    return branch, exam
