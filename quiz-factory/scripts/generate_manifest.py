#!/usr/bin/env python3
"""Build quiz-factory/manifest.json from current repo state.

Usage (repo root):
    python quiz-factory/scripts/generate_manifest.py
    python quiz-factory/scripts/generate_manifest.py --write
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHASES = ROOT / "phases"
OUT = ROOT / "quiz-factory" / "manifest.json"

PHASE_ORDER = ["07", "08", "10", "06", "09", "12", "13", "15", "16", "17", "18"]
LESSON_RE = re.compile(r"^[0-9]{2}-[a-z0-9][a-z0-9-]*[a-z0-9]$")
PHASE_RE = re.compile(r"^([0-9]{2})-")


def lesson_path(phase: Path, lesson: Path) -> str:
    return f"phases/{phase.name}/{lesson.name}"


def job_for_lesson(lesson: Path) -> str | None:
    quiz = lesson / "quiz.json"
    if not quiz.is_file():
        return "create_quiz"
    data = json.loads(quiz.read_text(encoding="utf-8"))
    if isinstance(data, list):
        questions = data
    elif isinstance(data, dict):
        questions = data.get("questions", [])
    else:
        questions = []
    for q in questions:
        if not str(q.get("explanation", "")).strip():
            return "fill_explanations"
    return None


def iter_lessons():
    for phase in sorted(PHASES.iterdir()):
        if not phase.is_dir():
            continue
        m = PHASE_RE.match(phase.name)
        if not m:
            continue
        phase_num = m.group(1)
        for lesson in sorted(phase.iterdir()):
            if lesson.is_dir() and LESSON_RE.match(lesson.name):
                yield phase_num, phase, lesson


def build_manifest() -> dict:
    rows = []
    for phase_num, phase, lesson in iter_lessons():
        job = job_for_lesson(lesson)
        if job is None:
            continue
        rows.append(
            {
                "path": lesson_path(phase, lesson),
                "phase": phase_num,
                "job_type": job,
                "status": "pending",
                "note": "",
            }
        )

    def sort_key(row: dict) -> tuple:
        try:
            order = PHASE_ORDER.index(row["phase"])
        except ValueError:
            order = 99
        return (order, row["path"])

    rows.sort(key=sort_key)
    create = sum(1 for r in rows if r["job_type"] == "create_quiz")
    fill = sum(1 for r in rows if r["job_type"] == "fill_explanations")
    return {
        "version": 1,
        "phase_order": PHASE_ORDER,
        "summary": {
            "pending_rows": len(rows),
            "create_quiz": create,
            "fill_explanations": fill,
        },
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help=f"write {OUT.relative_to(ROOT)}",
    )
    args = parser.parse_args()
    manifest = build_manifest()
    text = json.dumps(manifest, indent=2) + "\n"
    if args.write:
        OUT.write_text(text, encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    else:
        print(text)
    s = manifest["summary"]
    print(
        f"# pending={s['pending_rows']} create_quiz={s['create_quiz']} "
        f"fill_explanations={s['fill_explanations']}",
        file=__import__("sys").stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
