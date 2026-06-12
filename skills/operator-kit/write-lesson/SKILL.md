# /write-lesson

Draft a lesson doc (`docs/en.md`) for a GTM engineering curriculum stage.
Uses GLM-5.1 (reasoning). Active from Stage 01.

## When to invoke
- Stage 01 is running and needs lesson outlines or full lesson drafts
- User says "write the lesson for [topic]" or "draft [stage] content"
- A stage CONTEXT.md calls for lesson generation

## Chain

### Step 0 — Pre-flight
```bash
python3 -c "import openai" 2>/dev/null || { echo "ERROR: pip install openai"; exit 1; }
[ -n "$ZHIPUAI_API_KEY" ] || { echo "ERROR: ZHIPUAI_API_KEY not set — check .env"; exit 1; }
```

### Step 1 — Read context
```bash
TOPIC="${1:-GTM engineering fundamentals}"
STAGE_CONTEXT=$(cat stages/01-gtm-skeleton/CONTEXT.md 2>/dev/null || echo "No context found")
VARIABLES=$(cat vault/variable-registry.md 2>/dev/null | head -60)

# Write large context to temp files to avoid shell arg escaping issues
echo "$STAGE_CONTEXT" > /tmp/zai_stage_ctx.txt
echo "$VARIABLES" > /tmp/zai_vars.txt
```
Adjust the stage path to whatever stage is active.

### Step 2 — Call GLM-5.1 + write output
```bash
OUTPUT_DIR="stages/01-gtm-skeleton/output/lessons"
mkdir -p "$OUTPUT_DIR"
SLUG=$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')
OUTPUT_FILE="$OUTPUT_DIR/${SLUG}-draft.md"

python3 - "$TOPIC" /tmp/zai_stage_ctx.txt /tmp/zai_vars.txt <<'PYEOF' > "$OUTPUT_FILE"
import os, sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai package not installed. Run: pip install openai")
    sys.exit(1)

client = OpenAI(
    api_key=os.environ["ZHIPUAI_API_KEY"],
    base_url=os.environ.get("ZAI_BASE_URL", "https://api.z.ai/api/coding/paas/v4"),
)

topic = sys.argv[1] if len(sys.argv) > 1 else "GTM engineering fundamentals"
stage_context = open(sys.argv[2]).read() if len(sys.argv) > 2 else ""
variables = open(sys.argv[3]).read() if len(sys.argv) > 3 else ""

SYSTEM = """You are a GTM engineering curriculum author. You write clear, practical lesson docs for technical GTM practitioners — people who sit between sales/marketing and engineering. Your lessons:
- Lead with a practical problem the reader actually faces
- Explain concepts through real GTM scenarios (CRM integrations, attribution, pipeline data)
- Include concrete examples with tool names (Salesforce, HubSpot, Segment, dbt, etc.)
- End with clear learning outcomes and a bridge to the next lesson
- Use plain English, active voice, no jargon without explanation
- Format: markdown, H2 sections, code blocks where relevant"""

USER = f"""Write a full lesson doc for: {topic}

Stage context:
{stage_context[:2000] if stage_context else "No additional context provided."}

Structure:
## Overview
## Why This Matters for GTM Engineers
## Core Concepts
## Hands-On Example
## Common Mistakes
## Learning Outcomes
## What's Next"""

response = client.chat.completions.create(
    model="GLM-5.1",
    messages=[
        {"role": "system", "content": SYSTEM},
        {"role": "user",   "content": USER},
    ],
    max_tokens=4000,
    stream=True,
)
for chunk in response:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
print()
PYEOF
```

### Step 3 — Validate + report
```bash
BYTES=$(wc -c < "$OUTPUT_FILE" 2>/dev/null || echo 0)
if [ "$BYTES" -lt 200 ]; then
  echo "ERROR: output too small ($BYTES bytes) — likely API failure or truncation. Check $OUTPUT_FILE"
  exit 1
fi
SECTIONS=$(grep -c "^## " "$OUTPUT_FILE" 2>/dev/null || echo 0)
WORDS=$(wc -w < "$OUTPUT_FILE" 2>/dev/null || echo 0)
echo "Written: $OUTPUT_FILE ($WORDS words, $SECTIONS sections)"
[ "$SECTIONS" -lt 6 ] && echo "WARN: expected 6 sections, found $SECTIONS — check for truncation"
rm -f /tmp/zai_stage_ctx.txt /tmp/zai_vars.txt
```

## Notes
- GLM-5.1 is a reasoning model: internal thinking tokens are not visible, output starts after reasoning completes. Normal.
- If output is empty, increase `max_tokens` — reasoning consumed the budget. Use ≥ 500 minimum.
- Requires: `pip install openai` and `ZHIPUAI_API_KEY` + `ZAI_BASE_URL` in `.env` (gitignored).
