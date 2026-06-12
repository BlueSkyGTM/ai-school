# /quality-check

Curriculum audit: accuracy, gaps, source alignment, coverage.
Uses GLM-4.7. Active at Stage 09, callable earlier for spot checks.

## When to invoke
- Stage 09 quality pass is running
- A lesson or exercise needs accuracy review
- User says "check this", "audit", "does this match the source", "what's missing"
- After `/write-lesson` or `/write-exercise` produces a draft

## Chain

### Step 0 — Pre-flight
```bash
python3 -c "import openai" 2>/dev/null || { echo "ERROR: pip install openai"; exit 1; }
[ -n "$ZHIPUAI_API_KEY" ] || { echo "ERROR: ZHIPUAI_API_KEY not set — check .env"; exit 1; }
```

### Step 1 — Load target + sources
```bash
TARGET="${1:-stages/02-lesson-injection/output}"
[ -e "$TARGET" ] || { echo "ERROR: target not found: $TARGET"; exit 1; }

# Write content to temp files to avoid shell arg escaping issues
find "$TARGET" -name "*.md" | head -5 | xargs cat 2>/dev/null | head -300 > /tmp/zai_audit_target.txt
cat stages/00-b-gtm-content-mapping/output/source-citations.md 2>/dev/null | head -100 > /tmp/zai_audit_citations.txt
```

### Step 2 — Call GLM-4.7 + write audit report
```bash
OUTPUT_DIR="stages/09-quality-pass/output"
mkdir -p "$OUTPUT_DIR"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUTPUT_FILE="$OUTPUT_DIR/audit-${TIMESTAMP}.md"

python3 - /tmp/zai_audit_target.txt /tmp/zai_audit_citations.txt <<'PYEOF' > "$OUTPUT_FILE"
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

target_content = open(sys.argv[1]).read() if len(sys.argv) > 1 else ""
citations      = open(sys.argv[2]).read() if len(sys.argv) > 2 else ""

SYSTEM = """You are a curriculum quality auditor for a GTM engineering course.
You check lesson content for: factual accuracy, alignment with cited sources,
coverage gaps, unclear explanations, and unsupported claims.
Output a structured audit report: PASS / WARN / FAIL per criterion, with specific line references."""

USER = f"""Audit this curriculum content:

{target_content[:4000]}

Reference sources:
{citations[:2000]}

Report format:
## Accuracy — [PASS/WARN/FAIL]
[findings]
## Source Alignment — [PASS/WARN/FAIL]
[findings]
## Coverage Gaps — [list any]
## Unclear Explanations — [list any]
## Overall Verdict — [SHIP / REVISE / BLOCK]"""

response = client.chat.completions.create(
    model="GLM-4.7",
    messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": USER}],
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

### Step 3 — Validate + escalate
```bash
BYTES=$(wc -c < "$OUTPUT_FILE" 2>/dev/null || echo 0)
if [ "$BYTES" -lt 100 ]; then
  echo "ERROR: audit output too small ($BYTES bytes) — likely API failure"
  rm -f /tmp/zai_audit_target.txt /tmp/zai_audit_citations.txt
  exit 1
fi
echo "Audit written: $OUTPUT_FILE"

# Escalate BLOCK verdicts immediately
if grep -q "Overall Verdict — BLOCK" "$OUTPUT_FILE" 2>/dev/null; then
  echo ""
  echo "!!! BLOCK VERDICT — halting pipeline. Review $OUTPUT_FILE before proceeding to Stage 10."
  rm -f /tmp/zai_audit_target.txt /tmp/zai_audit_citations.txt
  exit 1
fi

rm -f /tmp/zai_audit_target.txt /tmp/zai_audit_citations.txt
echo "Verdict: $(grep 'Overall Verdict' "$OUTPUT_FILE" | head -1)"
```
