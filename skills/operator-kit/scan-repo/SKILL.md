# /scan-repo

Fast read-only codebase traversal. Maps structure, finds patterns, surfaces gaps.
Uses GLM-4.7-Flash (fast, low cost). Active from Stage 01+.

## When to invoke
- Need to understand what exists before building
- Looking for a file, pattern, or symbol across the repo
- Stage entry check: "what's already here for [topic]?"
- User says "scan", "find", "what do we have for", "check if X exists"

## Chain

### Step 0 — Pre-flight
```bash
python3 -c "import openai" 2>/dev/null || { echo "ERROR: pip install openai"; exit 1; }
[ -n "$ZHIPUAI_API_KEY" ] || { echo "ERROR: ZHIPUAI_API_KEY not set — check .env"; exit 1; }
```

### Step 1 — Collect file tree + target content
```bash
QUERY="${1:-summarize the repo structure}"
TREE=$(find . -not -path './.git/*' -not -path './node_modules/*' -not -path './.claude/*' \
  -not -path './graphify-out/*' -not -path './__pycache__/*' \
  | sort | head -200)
# Pull content of files that match the query topic
RELEVANT=$(grep -rl "$QUERY" stages/ vault/ references/ skills/ 2>/dev/null | head -10)
CONTENT=""
for f in $RELEVANT; do
  CONTENT="$CONTENT\n\n--- $f ---\n$(head -40 $f)"
done

# Write to temp files
printf '%s' "$TREE" > /tmp/zai_scan_tree.txt
printf '%b' "$CONTENT" > /tmp/zai_scan_content.txt
```

### Step 2 — Call GLM-4.7-Flash
```bash
python3 - "$QUERY" /tmp/zai_scan_tree.txt /tmp/zai_scan_content.txt <<'PYEOF'
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

query   = sys.argv[1] if len(sys.argv) > 1 else "summarize the repo structure"
tree    = open(sys.argv[2]).read() if len(sys.argv) > 2 else ""
content = open(sys.argv[3]).read() if len(sys.argv) > 3 else ""

SYSTEM = """You are a codebase navigator for a GTM engineering curriculum project.
You read file trees and content snippets and give concise, actionable summaries.
Report: what exists, what's missing, what needs attention. Be specific with file paths."""

USER = f"""Query: {query}

File tree (first 200 entries):
{tree[:3000]}

Relevant file content:
{content[:3000]}

Answer the query. Be specific. Include file paths. Flag any gaps relevant to the query."""

response = client.chat.completions.create(
    model="GLM-4.7-Flash",
    messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": USER}],
    max_tokens=1000,
    stream=True,
)
for chunk in response:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
print()
PYEOF

rm -f /tmp/zai_scan_tree.txt /tmp/zai_scan_content.txt
```

### Step 3 — Report
Output goes directly to Claude Code (no file write — scan is read-only).
Claude Code uses the result to decide next steps.

## Notes
- GLM-4.7-Flash: standard model (not reasoning), fast responses, low token cost.
- Read-only: this skill never writes files.
- For deep code analysis use `/quality-check` instead.
