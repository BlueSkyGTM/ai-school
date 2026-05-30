# Quiz factory — batch operator (Claude Code)

You are a **batch worker**, not a tutor. Do not chat, ask questions, or redesign lessons.

**Gate:** `.cursor/rules/lesson-planning-gate.mdc` applies to every row you process.

## Mission

Process `manifest.json` rows with `status: pending` in phase order. For each row:

1. Follow [lesson-planning](../.cursor/skills/lesson-planning/SKILL.md) (alignment, difficulty, seven insights).
2. Run loops in [ARCHITECTURE.md](ARCHITECTURE.md).
3. Pass Tier A audit for that lesson.
4. Commit **one lesson directory only**.
5. Set manifest row to `done` (or `blocked` with reason).

## Hard rules

- **Read first:** [lesson-planning SKILL](../.cursor/skills/lesson-planning/SKILL.md) → [CONTEXT.md](CONTEXT.md) → [REFERENCES.md](REFERENCES.md) → [ARCHITECTURE.md](ARCHITECTURE.md).
- **Before each new phase:** read `phases/NN-*/BATCH.md`; use lesson-planning **seven insights** to compare output.
- **Do not** copy flagship `quiz.json` text — extract claims from **that** lesson’s doc/code (see skill).
- **Variance rule (mold):** the six `correct` values must not be a constant column; vary the correct slot (REFERENCES.md "Variance rule"). Leave position-dependent options ("all of the above", "both B and C") in place.
- **`redo_quiz` rows:** rebuild questions from the doc/code — the existing text is an anti-pattern (all answer `A`), do not trust it.
- **Edit only** `phases/.../MM-lesson/quiz.json` unless `job_type` says otherwise.
- **Never** edit `docs/en.md`, `code/`, `README.md`, or `site/data.js`.
- **Never** batch multiple lessons in one commit.
- **Never** skip audit because the quiz "looks fine."
- On audit fail: fix quiz, re-audit, max **2** retries → then `blocked` and continue.
- Append one line per lesson to `run.log`: `ISO8601 | path | done|blocked | commit or error`.

## Phase layers

Before processing phase `NN`, read:

`phases/NN-*-slug/BATCH.md` if it exists, else `templates/PHASE-BATCH.md` (defaults only).

## Commit format

```text
feat(phase-NN/MM): add <lesson-slug> quiz
```

For explanation-only jobs:

```text
fix(phase-NN/MM): fill quiz explanations
```

## Stop conditions

- All rows for the assigned phase slice are `done` or `blocked`.
- User message says stop.
- Do not stop early because a row is tedious.

## When blocked

Write `blocked` + short reason in manifest. Do not invent quiz content from general knowledge — only from that lesson's `docs/en.md` and `code/`.
