pending/batch-006-phase14-01-09.md

---

## Status after upstream sync — 2026-06-03

Pulled 307 files from `rohitg00/ai-engineering-from-scratch`:
- **30 new Phase 19 lessons** (lessons 58–87): ViT, cross-attention, DDP, ZeRO, pipeline parallel, safety gate, RAG eval, jailbreak taxonomy, and more
- **200 quiz.json files** with 1,109 questions total — this was the "200+ quizzes" roadmap item. Data exists. UI integration still needed.

### What this eliminated
- Creating quiz content from scratch — **done**, data is pulled
- Building Phase 19 capstone lesson files — **done**, 30 new lessons exist

### What still needs doing

#### Schema repair (existing batches — still valid)
| Batches | Phase | Files | Issue |
|---------|-------|-------|-------|
| 001–005 | 05-nlp | 29 files | 8q → trim to 6q |
| 006–010 | 14-agent-engineering | 42 files | 7q → trim to 6q |

#### Schema repair (new — not yet batched)
| Phase | Files | Issue |
|-------|-------|-------|
| 00-setup-and-tooling | 12 | 5q — needs audit (may need 1 check question added) |
| 01-math-foundations | 22 | 5q — same |
| 04-computer-vision | 28 | 5q — same |
| 07-transformers | 1 | 5q |
| 11-llm-engineering | 4 | 5q |
| 16-multi-agent | 2 | 5q |
| 17-infrastructure | 1 | 7q → trim |
| 19-capstone-projects | 21 | 7q → trim (new lessons 58–87) |

#### Site integration (not yet built)
- Quiz UI in lesson reader — questions are data, no page renders them yet
- data.js sync — Phase 19 lessons 58–87 exist in `phases/` but not yet indexed in `site-new/js/data.js`

### 134 quizzes already correct — no work needed on those
