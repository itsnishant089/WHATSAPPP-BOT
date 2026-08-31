"""Build Excel knowledge files from the WhatsApp bot kit CSVs."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parent.parent
KIT = ROOT.parent / "whatsapp-bot-kit"
DATA = ROOT / "data"

HEADERS = [
    "category",
    "subcategory",
    "title",
    "question",
    "answer",
    "keywords",
    "url",
    "branch",
    "exam",
    "priority",
    "active",
]


def _priority(value: str) -> int:
    text = (value or "").upper()
    if "HIGH" in text:
        return 20
    try:
        return int(value)
    except (TypeError, ValueError):
        return 10


def _infer_branch(text: str) -> str:
    lowered = text.lower()
    mapping = [
        ("computer", "CSE"),
        ("cse", "CSE"),
        ("mechanical", "Mechanical"),
        ("civil", "Civil"),
        ("electrical", "Electrical"),
        ("ece", "ECE"),
        ("ai & ml", "AI & ML"),
        ("automobile", "Automobile"),
    ]
    for needle, branch in mapping:
        if needle in lowered:
            return branch
    return ""


def _infer_exam(text: str) -> str:
    lowered = text.lower()
    if "leet" in lowered or "ocet" in lowered:
        return "HSBTE LEET"
    if "diploma" in lowered or "hsbte" in lowered or "pyq" in lowered:
        return "HSBTE Diploma"
    return ""


def write_xlsx(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "knowledge"
    ws.append(HEADERS)
    for row in rows:
        ws.append([row.get(h, "") for h in HEADERS])
    wb.save(path)


def load_faq(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            category = (raw.get("Category") or "").strip()
            keywords = raw.get("Trigger_Keywords") or ""
            answer = raw.get("Full_Answer") or ""
            url = (raw.get("Links_To_Send") or "").split("|")[0].strip()
            blob = f"{category} {keywords} {answer}"
            rows.append(
                {
                    "category": category or "faq",
                    "subcategory": "",
                    "title": category,
                    "question": category,
                    "answer": answer,
                    "keywords": keywords,
                    "url": url,
                    "branch": _infer_branch(blob),
                    "exam": _infer_exam(blob),
                    "priority": _priority(raw.get("Priority") or ""),
                    "active": True,
                }
            )
    return rows


def load_resources(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            category = (raw.get("Category") or "").strip()
            name = raw.get("Name") or ""
            desc = raw.get("Description") or ""
            notes = raw.get("Notes") or ""
            keywords = raw.get("Keywords") or ""
            url = raw.get("URL") or ""
            blob = f"{category} {name} {desc} {keywords} {notes}"
            answer = "\n".join(p for p in (desc, notes, url) if p)
            rows.append(
                {
                    "category": category,
                    "subcategory": notes,
                    "title": name,
                    "question": desc,
                    "answer": answer,
                    "keywords": keywords,
                    "url": url,
                    "branch": _infer_branch(blob),
                    "exam": _infer_exam(blob),
                    "priority": 8 if "PDF" in category else 5,
                    "active": True,
                }
            )
    return rows


def main() -> int:
    faq_csv = KIT / "Sheet1_FAQ_WhatsApp_Bot.csv"
    res_csv = KIT / "Sheet2_All_Pages_Resources_URLs.csv"
    if not faq_csv.exists() or not res_csv.exists():
        print("Kit CSVs not found next to this project.", file=sys.stderr)
        return 1
    faq = load_faq(faq_csv)
    resources = load_resources(res_csv)
    syllabus = [r for r in resources if "syllabus" in (r["category"] or "").lower()]
    pyq = [r for r in resources if "pyq" in (r["category"] or "").lower()]
    premium = [r for r in resources if "premium" in (r["category"] or "").lower()]
    responses = [r for r in faq if r["category"] in {"Greeting", "Doubt / Unknown", "Contact"}]
    knowledge = faq + resources
    write_xlsx(DATA / "faq.xlsx", faq)
    write_xlsx(DATA / "resources.xlsx", resources)
    write_xlsx(DATA / "syllabus.xlsx", syllabus)
    write_xlsx(DATA / "pyq.xlsx", pyq)
    write_xlsx(DATA / "premium.xlsx", premium)
    write_xlsx(DATA / "responses.xlsx", responses)
    write_xlsx(DATA / "knowledge.xlsx", knowledge)
    print(f"Wrote Excel files under {DATA} ({len(knowledge)} combined rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
