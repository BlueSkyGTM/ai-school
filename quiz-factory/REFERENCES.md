# References

## Schema (canonical)

From `AGENTS.md` — every `quiz.json`:

```json
{
  "lesson": "<dir-slug>",
  "title": "<Lesson Title>",
  "questions": [
    {"stage": "pre", "question": "...", "options": ["a","b","c","d"], "correct": 0, "explanation": "..."},
    {"stage": "check", "question": "...", "options": ["a","b","c","d"], "correct": 1, "explanation": "..."},
    {"stage": "check", "question": "...", "options": ["a","b","c","d"], "correct": 2, "explanation": "..."},
    {"stage": "check", "question": "...", "options": ["a","b","c","d"], "correct": 1, "explanation": "..."},
    {"stage": "post", "question": "...", "options": ["a","b","c","d"], "correct": 3, "explanation": "..."},
    {"stage": "post", "question": "...", "options": ["a","b","c","d"], "correct": 0, "explanation": "..."}
  ]
}
```

- `correct`: zero-based index into `options`
- 2–6 options per question
- No legacy keys: `q`, `choices`, `answer`
- No substring `placeholder` in option text (Tier B / `--strict-quiz`)

## Difficulty bar (one paragraph)

- **pre**: recall from hook + objectives (one step).
- **check**: apply the lesson's main mechanism; distractors = plausible mistakes from `docs/en.md`.
- **post**: integrate two ideas from the lesson or compare to prerequisite concept.
- **explanation**: 1–3 sentences; cite the lesson's terms; say why wrong options fail.

## Pedagogy (read before first draft)

| Doc | Content |
|-----|---------|
| [lesson-planning SKILL](../.cursor/skills/lesson-planning/SKILL.md) | Seven insights, planning, review, triage |
| [QUALITY-RUBRIC.md](QUALITY-RUBRIC.md) | PM spot-check after each phase |

## Gold JSON (read live — insights in skill)

See **Seven insights** in lesson-planning for paths. Also: `phases/04-computer-vision/04-image-classification/quiz.json`, `phases/19-capstone-projects/54-paper-writer/quiz.json`.

## Scrape order (per lesson)

1. `docs/en.md` — title, objectives, key sections
2. `code/main.*` or primary source — function names, invariants, outputs
3. `outputs/*.md` — optional tone; do not copy blindly
4. Neighbor quiz in same phase if present

## Validation commands

From repo root:

```bash
python scripts/audit_lessons.py
python scripts/audit_lessons.py --strict-quiz
```

After one lesson (optional narrow check — audit still scans all lessons):

```bash
python scripts/audit_lessons.py
```

## Title field

Copy lesson title from `docs/en.md` H1 or frontmatter; match README lesson name when obvious.
