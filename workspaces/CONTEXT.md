# Current State — AI Engineering School
**Last updated:** 2026-06-03

---

## What is done

### Curriculum
- 498 lessons across 20 phases (30 new Phase 19 capstone lessons added today)
- All lesson content exists — no missing lessons to create
- 1,109 quiz questions across 200+ files pulled from upstream
- Quiz creation is COMPLETE — do not write quiz creation batches

### Portfolio site (`site-new/`)
- All 6 pages built and working: Home, Course, Catalog, Library, Projects, Glossary
- Progress tracking via localStorage (adapter-ready for WordPress REST)
- 110 library resources with type filter (Book/Video/Course/Paper/Article/Interactive)
- XP/level/rank system (7 tiers: Initiate → AI Architect)
- All 60 capstone projects surfaced on Projects page
- Mobile nav fixed, command palette working, no JS errors
- WordPress plugin + page template written at `site-new/wordpress/`
- README written and pushed to https://github.com/BlueSkyGTM/ai-school

---

## What still needs doing

### P0 — Schema repair (Cline executes from batches)

162 quiz.json files need normalisation to the 6-question canonical schema.
Batches 001-010 in `cline-backlog/batches/pending/` cover phases 05 and 14.
New batches needed for the remaining phases.

| Phase | Files | Issue | Status |
|-------|-------|-------|--------|
| 00-setup-and-tooling | 12 | 5q | No batch yet |
| 01-math-foundations | 22 | 5q | No batch yet |
| 04-computer-vision | 28 | 5q | No batch yet |
| 05-nlp | 29 | 8q → 6q | Batches 001-005 written |
| 07-transformers | 1 | 5q | No batch yet |
| 11-llm-engineering | 4 | 5q | No batch yet |
| 14-agent-engineering | 42 | 7q → 6q | Batches 006-010 written |
| 16-multi-agent | 2 | 5q | No batch yet |
| 17-infrastructure | 1 | 7q → 6q | No batch yet |
| 19-capstone-projects | 21 | 7q → 6q | No batch yet |

**Active batch:** `pending/batch-006-phase14-01-09.md`

For 5q files: audit each to determine if they need 1 question added or different handling.
For 7-8q files: trim per existing batch pattern.

### P1 — WordPress deployment

Plugin and template are written. Need to install on a WordPress instance.
Files: `ai-school-curriculum/site-new/wordpress/`
- `aischool-progress.php` — REST plugin (`/wp-json/aischool/v1/progress`)
- `page-aischool.php` — page template for Course/Catalog/Library/Projects/Glossary

### P2 — 5q quiz files (content creation required — NOT simple repair)

69 files across phases 00, 01, 04, 07, 11, 16 have pattern `pre, pre, post, post, post`.
Target is `pre, check, check, check, post, post`. These need 3 check questions WRITTEN
per lesson — that is quiz creation, not trimming. 69 × 3 = 207 new questions.
Decision pending: write them, or leave as non-standard until later.

### P3 — lesson.html (skeleton, not functional)

The catalog links to `lesson.html?path=phases/...` for lessons that have GitHub URLs.
Currently clicking a catalog row opens a non-rendering skeleton page.
Two options:
- A) Redirect to GitHub URL (10 lines JS, simple)
- B) Fetch and render lesson markdown (full lesson reader build, larger)

### P4 — Homepage copy

`index.html` signpost cards still say "470+" lessons. Should be "498".

### P5 — Close upstream PRs

Two open PRs from BlueSkyGTM on `rohitg00/ai-engineering-from-scratch`:
- #236 "feat: add quiz.json for seven orphan lessons" — superseded by upstream pull
- #237 "docs: wire orphan lessons into README and ROADMAP" — check if still relevant
Close or update them.

### P6 — Quiz UI (future)

1,109 questions exist as JSON. Nothing renders them yet. Build a quiz interface
into the lesson reader when WordPress is deployed.

### P7 — Graphify (future)

Interactive prerequisite DAG for the site. Shows chapter dependencies visually.

---

## Known gaps (do not skip)

1. **data.js lesson count** — index.html signpost cards say "470+" but site has 498 lessons.
   Fix: update copy in `site-new/index.html` signpost descriptions. (P4 above)

2. **5q quiz files** — 69 files have no check questions at all. Pattern: `pre, pre, post, post, post`.
   These cannot be fixed by trimming — they need 3 check questions written per lesson.
   Do NOT brief Cline on these without explicit approval and content direction.

2. **Stage sequence not enforced by CI** — manually verify `pre, check, check, check, post, post`
   before every schema repair commit until the audit script is updated.

---

## How to brief Cline

1. Write `cline-backlog/batches/pending/batch-NNN-description.md`
2. Set `cline-backlog/batches/ACTIVE.md` → relative path to that file
3. Hand off to Cline: "read ACTIVE.md and execute"
4. Cline commits per lesson, you review

Every brief needs a locked JSON skeleton. Cline never invents structure.

Gold reference quizzes (style anchors — never copy content):
- `phases/07-transformers-deep-dive/16-speculative-decoding/quiz.json`
- `phases/10-llms-from-scratch/34-gradient-checkpointing/quiz.json`
- `phases/19-capstone-projects/54-paper-writer/quiz.json`
