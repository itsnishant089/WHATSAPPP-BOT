from pathlib import Path

from openpyxl import Workbook

from app.services.excel_service import ExcelService


def _write(path: Path, rows: list[list[object]]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.append(
        [
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
    )
    for row in rows:
        ws.append(row)
    wb.save(path)


def test_excel_search(tmp_path: Path):
    _write(
        tmp_path / "knowledge.xlsx",
        [
            [
                "syllabus",
                "CSE",
                "HSBTE Diploma CSE Syllabus",
                "Where can I find CSE syllabus?",
                "Official CSE syllabus PDF is here.",
                "cse, syllabus, computer, hsbte",
                "https://hsbteleet.com/hsbte-syllabus",
                "CSE",
                "HSBTE Diploma",
                10,
                True,
            ],
            [
                "pyq",
                "Mechanical",
                "Mechanical PYQ",
                "mechanical ke PYQ",
                "Mechanical PYQ hub",
                "mechanical, pyq",
                "https://hsbteleet.com/mech",
                "Mechanical",
                "HSBTE Diploma",
                8,
                True,
            ],
        ],
    )
    service = ExcelService(tmp_path)
    service.load()
    cse = service.search("CSE ka syllabus")
    assert cse
    assert "syllabus" in cse[0].title.lower() or "cse" in cse[0].keywords.lower()
    mech = service.search("mechanical ke PYQ")
    assert mech
    assert "mechanical" in mech[0].title.lower() or "mechanical" in mech[0].keywords.lower()
    leet = service.search("LEET eligibility kya hai")
    assert isinstance(leet, list)
