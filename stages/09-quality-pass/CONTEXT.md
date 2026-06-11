<!-- Agent: Hypatia -->
# Stage 09: Quality Pass

Audit double-helix alignment and GTM accuracy. Lyra fills identified gaps directly into Stage 02 output.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| All hybrid lessons | `../02-lesson-injection/output/hybrid-lessons/` | Full curriculum | What to audit |
| GTM topic map | `../00-b-gtm-content-mapping/output/gtm-topic-map.md` | Full file | Alignment reference |
| Source citations | `../00-b-gtm-content-mapping/output/source-citations.md` | Full file | GTM accuracy check |
| GTM handbook | `../../shared/gtm-handbook-extract.md` | Full file | Authoritative GTM definitions — verify lesson toolstacks, KPIs, and workflows match the playbook |
| MLOps appendage | `../../shared/mlops-appendage-concepts.md` | Full file | Verify appendage lessons are placed after Phase 17 and match Made With ML source content |
| GTM Starter Kit | `../../shared/gtm-starter-kit-guide.md` | Skills table | Verify key phases (01, 02, 03, 05, 17) have GTM Starter Kit exercise hooks |
| Helix voice | `../../vault/helix-voice.md` | Full file | Voice consistency check |
| Quality standards | `../../shared/quality-standards.md` | Full file | Master quality reference for all four dimensions |
| Lesson judge prompts | `../../shared/quality-evaluator/lesson-judge-prompts.md` | Full file | CLARITY_JUDGE, WEAVE_JUDGE, ACCURACY_JUDGE — run per lesson |

## Process

1. Run CLARITY_JUDGE on every lesson — flag lessons scoring < 3.0 overall
2. Run WEAVE_JUDGE on every lesson — flag lessons where derivation < 3.0 or ## Sources missing
3. Run ACCURACY_JUDGE on every lesson — flag lessons scoring < 3.5 overall
4. Audit voice consistency: compare lesson tone across all phases against helix-voice.md — flag any phase cluster where Lyra drifted from the established voice benchmark
5. Identify gaps: phases with thin or missing GTM content
6. Lyra fills gaps per gtm-topic-map guidance — writes filled lessons back to `../02-lesson-injection/output/hybrid-lessons/`

## Audit

| Check | Pass Condition |
|-------|---------------|
| Alignment score | Every phase has at least one woven GTM-AI connection |
| Accuracy verified | No GTM claim lacks a citation from source-citations.md |
| Voice consistent | No phase cluster deviates from the Helix voice benchmark in helix-voice.md |
| Gaps filled | All identified gaps have corresponding filled lesson files in Stage 02 output |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| `curriculum-audit-report.md` | `output/` | Alignment scores, gap list, fill actions taken |
| Gap-filled lessons | `../02-lesson-injection/output/hybrid-lessons/` | Written in place — Stage 10 reads this path |
