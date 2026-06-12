# /write-exercise

Generate exercise specs for a GTM engineering curriculum lesson.
Uses GLM-5.1 (reasoning). Active from Stage 03.

## When to invoke
- Stage 03 exercise design is running
- A lesson draft exists and needs hands-on practice tasks
- User says "write exercises for [lesson]", "build the exercise for [topic]"

## Chain

### Step 0 — Pre-flight
```bash
python3 -c "import openai" 2>/dev/null || { echo "ERROR: pip install openai"; exit 1; }
[ -n "$ZHIPUAI_API_KEY" ] || { echo "ERROR: ZHIPUAI_API_KEY not set — check .env"; exit 1; }
```

### Step 1 — Read lesson content
```bash
LESSON="${1:-}"
[ -f "$LESSON" ] || { echo "ERROR: lesson file not found: $LESSON"; exit 1; }
TOPIC=$(head -3 "$LESSON" 2>/dev/null | grep "^#" | sed 's/^#*//' | xargs)

# Write content to temp file to avoid shell arg escaping issues
cp "$LESSON" /tmp/zai_lesson_content.txt
```

### Step 2 — Call GLM-5.1 + write output
```bash
OUTPUT_DIR="stages/03-exercise-design/output"
mkdir -p "$OUTPUT_DIR"
SLUG=$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')
OUTPUT_FILE="$OUTPUT_DIR/${SLUG}-exercises.md"

python3 - "$TOPIC" /tmp/zai_lesson_content.txt <<'PYEOF' > "$OUTPUT_FILE"
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

topic = sys.argv[1] if len(sys.argv) > 1 else ""
lesson_content = open(sys.argv[2]).read() if len(sys.argv) > 2 else ""

SYSTEM = """You design practical exercises for GTM engineering students. Each exercise:
- Ties directly to a lesson's learning outcomes (never generic)
- Uses realistic GTM scenarios: data pipelines, CRM config, attribution logic, reporting
- Has a clear setup, task, expected output, and success criteria
- Includes a worked example and common failure modes
- Is completable in 20-45 minutes"""

USER = f"""Design 2-3 exercises for this lesson:

Topic: {topic}

Lesson content:
{lesson_content[:3000]}

For each exercise provide:
## Exercise [N]: [Name]
**Time:** [estimate]
**Scenario:** [realistic GTM context]
**Setup:** [what the student has before starting]
**Task:** [what they must do]
**Expected Output:** [what correct completion looks like]
**Success Criteria:** [how to verify]
**Worked Example:** [abbreviated solution path]
**Common Mistakes:** [2-3 failure modes]"""

response = client.chat.completions.create(
    model="GLM-5.1",
    messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": USER}],
    max_tokens=3000,
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
  echo "ERROR: output too small ($BYTES bytes) — likely API failure. Check $OUTPUT_FILE"
  rm -f /tmp/zai_lesson_content.txt
  exit 1
fi
EXERCISES=$(grep -c "^## Exercise" "$OUTPUT_FILE" 2>/dev/null || echo 0)
echo "Written: $OUTPUT_FILE ($EXERCISES exercises)"
[ "$EXERCISES" -lt 2 ] && echo "WARN: expected 2-3 exercises, found $EXERCISES — check for truncation"
rm -f /tmp/zai_lesson_content.txt
```
