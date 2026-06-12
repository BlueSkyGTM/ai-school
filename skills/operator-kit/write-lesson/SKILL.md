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
[ -f "stages/00-c-agent-setup/output/agent-briefs/lyra-content-brief.md" ] || { echo "ERROR: lyra-content-brief.md missing — run Stage 00-c first"; exit 1; }
```

### Step 1 — Read context (governed maze: extract only what GLM needs)
```bash
TOPIC="${1:-GTM engineering fundamentals}"
GTM_CLUSTER="${2:-}"  # optional: named cluster from gtm-topic-map.md

# Extract the four sections GLM needs from the brief — not the whole file
# Six-beat structure + tone rules + GTM redirect rules + what NOT to do
BRIEF=$(python3 -c "
import re, sys
text = open('stages/00-c-agent-setup/output/agent-briefs/lyra-content-brief.md').read()
sections = ['## Format: Six-Beat Lesson Structure', '## GTM Redirect Rules',
            '## Tone Rules', '## What NOT To Do', '## Code Rules',
            '## Learning Objectives Rules']
out = []
for s in sections:
    m = re.search(re.escape(s) + r'(.*?)(?=\n## |\Z)', text, re.DOTALL)
    if m:
        out.append(s + m.group(1).rstrip())
print('\n\n'.join(out))
" 2>/dev/null | head -120)  # cap at ~400 tokens

# Topic map cluster for this lesson (1-2 relevant lines only)
CLUSTER_CONTEXT=""
if [ -n "$GTM_CLUSTER" ]; then
    CLUSTER_CONTEXT=$(grep -A2 "$GTM_CLUSTER" stages/00-b-gtm-content-mapping/output/gtm-topic-map.md 2>/dev/null | head -5)
fi

# Write to /tmp — no shell escaping issues, no repo context bleed
echo "$BRIEF" > /tmp/zai_brief.txt
echo "$CLUSTER_CONTEXT" > /tmp/zai_cluster.txt
```
Adjust the stage path to whatever stage is active.

### Step 2 — Call GLM-5.1 + write output
```bash
OUTPUT_DIR="stages/01-gtm-skeleton/output/lessons"
mkdir -p "$OUTPUT_DIR"
SLUG=$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')
OUTPUT_FILE="$OUTPUT_DIR/${SLUG}-draft.md"

python3 - "$TOPIC" /tmp/zai_brief.txt /tmp/zai_cluster.txt <<'PYEOF' > "$OUTPUT_FILE"
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["ZHIPUAI_API_KEY"],
    base_url=os.environ.get("ZAI_BASE_URL", "https://api.z.ai/api/coding/paas/v4"),
)

topic        = sys.argv[1] if len(sys.argv) > 1 else "GTM engineering fundamentals"
brief        = open(sys.argv[2]).read() if len(sys.argv) > 2 else ""
cluster_ctx  = open(sys.argv[3]).read() if len(sys.argv) > 3 else ""

# System prompt: Lyra identity + hard constraints distilled from the brief
SYSTEM = """You are Lyra, a GTM engineering curriculum author. Rules:
- Peer-to-peer tone. The student is a practitioner, not a student.
- Mechanism before tool. Explain the algorithm/pattern first, then name the tool.
- No marketing claims. "Clay is powerful" is banned. "Clay implements a waterfall" is correct.
- No scaffolded code. All code must run unmodified and produce observable output.
- No objectives starting with "Understand", "Learn", or "Know".
- If a GTM citation is missing, write [CITATION NEEDED — concept: ...] not an invention.
- No section may be omitted from the six-beat structure."""

USER = f"""Write a lesson OUTLINE for: {topic}

Six-beat structure and rules (follow exactly):
{brief}

GTM cluster context for "Use It" section:
{cluster_ctx if cluster_ctx.strip() else "Use the closest matching GTM application for this AI concept."}

Output: beat headings + 1-2 sentence description per beat. No full prose. Exercise hooks only (easy/medium/hard), not full exercise text."""

response = client.chat.completions.create(
    model="GLM-5.1",
    messages=[
        {"role": "system", "content": SYSTEM},
        {"role": "user",   "content": USER},
    ],
    max_tokens=2000,
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
[ "$SECTIONS" -lt 7 ] && echo "WARN: expected ≥7 sections (six-beat + key terms), found $SECTIONS — check for truncation"

# Check six-beat compliance
for BEAT in "Learning Objectives" "The Problem" "The Concept" "Build It" "Use It" "Ship It" "Exercises"; do
  grep -q "## $BEAT" "$OUTPUT_FILE" 2>/dev/null || echo "WARN: missing beat '## $BEAT'"
done

rm -f /tmp/zai_brief.txt /tmp/zai_cluster.txt
```

## Notes
- GLM-5.1 is a reasoning model: thinking tokens are invisible, output starts after reasoning completes. Normal.
- If output is empty, increase `max_tokens` — reasoning consumed the budget. Minimum 500.
- The brief is loaded at runtime from `stages/00-c-agent-setup/output/agent-briefs/lyra-content-brief.md`. If it changes, the skill picks up the change automatically on next invocation.
- Requires: `pip install openai` and `ZHIPUAI_API_KEY` + `ZAI_BASE_URL` in `.env` (gitignored).
- Governed maze: only 4 sections of the brief (~400 tokens) are passed to GLM, not the full file. Claude Code reads the full brief; GLM receives the task-specific extract.
