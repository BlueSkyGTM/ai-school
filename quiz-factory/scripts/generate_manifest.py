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

# Quizzes generated as the all-"A" anti-pattern (every correct=0). Positions were
# mechanically balanced, but the content is unverified — Claude Code must rebuild
# them from docs/en.md + code/ with the variance rule. See REFERENCES.md "Anti-pattern".
REDO_QUIZ = {
    "phases/07-transformers-deep-dive/15-attention-variants",
    "phases/07-transformers-deep-dive/16-speculative-decoding",
    "phases/08-generative-ai/19-visual-autoregressive-var",
    "phases/10-llms-from-scratch/15-speculative-decoding-eagle3",
    "phases/10-llms-from-scratch/16-differential-attention-v2",
    "phases/10-llms-from-scratch/17-native-sparse-attention",
    "phases/10-llms-from-scratch/34-gradient-checkpointing",
}
REDO_NOTE = "all-A anti-pattern; rebuild questions + variance from docs/en.md and code/"


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
        path = lesson_path(phase, lesson)
        if path in REDO_QUIZ:
            job, note = "redo_quiz", REDO_NOTE
        else:
            job, note = job_for_lesson(lesson), ""
        if job is None:
            continue
        rows.append(
            {
                "path": path,
                "phase": phase_num,
                "job_type": job,
                "status": "pending",
                "note": note,
            }
        )

    # redo_quiz first (broken in production), then phase order, then path.
    job_rank = {"redo_quiz": 0}

    def sort_key(row: dict) -> tuple:
        try:
            order = PHASE_ORDER.index(row["phase"])
        except ValueError:
            order = 99
        return (job_rank.get(row["job_type"], 1), order, row["path"])

    rows.sort(key=sort_key)
    create = sum(1 for r in rows if r["job_type"] == "create_quiz")
    fill = sum(1 for r in rows if r["job_type"] == "fill_explanations")
    redo = sum(1 for r in rows if r["job_type"] == "redo_quiz")
    return {
        "version": 1,
        "phase_order": PHASE_ORDER,
        "summary": {
            "pending_rows": len(rows),
            "redo_quiz": redo,
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
        f"# pending={s['pending_rows']} redo_quiz={s['redo_quiz']} "
        f"create_quiz={s['create_quiz']} fill_explanations={s['fill_explanations']}",
        file=__import__("sys").stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
