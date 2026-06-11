<!-- Agent: Lyra-code -->
# Stage 06: Site Readability Overhaul

Implement modular lesson components without breaking the existing render pipeline.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Design system snapshot | `../00-a-curriculum-archaeology/output/design-system-snapshot.md` | Full file | Rendering stack + existing patterns to extend |
| Hybrid lessons | `../02-lesson-injection/output/hybrid-lessons/` | Sample lessons | Before/after reference |
| Render pipeline | `{{REPO_URL}}` | ui.js, catalog.js | Do not break these |
| Lyra code brief | `../00-c-agent-setup/output/agent-briefs/lyra-code-brief.md` | Full file | Site architecture constraints |
| Illustration pipeline | `../../shared/illustration-pipeline.md` | Full file | Tier 1+2 illustration generation for The Concept beats |
| Quality standards | `../../shared/quality-standards.md` | Illustration Quality section | Tier selection logic and validation requirements |

## Prerequisites

**GLM-image swap must be implemented before this stage runs.** `scripts/generate-image.ts` in smart-illustrator must have the Gemini SDK replaced with the GLM-image API call (see illustration-pipeline.md → Tier 1 implementation notes). Stage 06 will fail if this is not done. Confirm by running one test generation call before starting.

## Process

1. Run /design-review on current site — 80-item audit
2. Prioritize: lessons that look thin, unreadable, or not visually significant
3. Confirm Mermaid rendering is wired: the site must parse ` ```mermaid ` fenced blocks and render them as SVG (mermaid.js CDN include or SSG plugin). If not already present, add it. Verify with one test block before proceeding.
4. Implement modular lesson components per the rendering stack from design-system-snapshot — do not break the existing render pipeline
5. Generate Tier 1 (GLM-image) and Tier 2 (Excalidraw) illustrations — per illustration-pipeline.md tier selection logic:
   - Run sequentially, not in parallel (two Playwright instances on the same machine will conflict)
   - Checkpoint each lesson's illustration status to `output/illustrations/progress.json` before moving to the next — resume from checkpoint on failure
   - Do not batch-queue Tier 2 (Excalidraw) — run render-and-inspect per lesson, write output, advance
6. Drop illustration outputs into `output/illustrations/{{PHASE}}/{{LESSON}}/` with alt-text as specified in illustration-pipeline.md
7. Validate all illustrations and site components in browser before /review gate

## Audit

| Check | Pass Condition |
|-------|---------------|
| Render pipeline intact | ui.js and catalog.js behavior unchanged |
| Lessons look significant | No lesson renders as a thin block of text |
| Components are modular | Each component can be updated independently |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| `site-components/` | `output/` | Updated lesson HTML components |
