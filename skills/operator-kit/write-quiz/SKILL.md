# /write-quiz

Generate FSRS-ready quiz banks for a lesson. Questions grounded in lesson content only.
Uses GLM-5.1 (reasoning). Active from Stage 04.

## When to invoke
- Stage 04 quiz/recall design is running
- A lesson doc exists and needs quiz questions
- User says "write quiz for [lesson]", "generate questions for [topic]"
- Never run before the lesson's `docs/en.md` objectives are confirmed

## Chain

### Step 0 — Pre-flight
```bash
python3 -c "import openai" 2>/dev/null || { echo "ERROR: pip install openai"; exit 1; }
[ -n "$ZHIPUAI_API_KEY" ] || { echo "ERROR: ZHIPUAI_API_KEY not set — check .env"; exit 1; }
```

### Step 1 — Read lesson + objectives
```bash
LESSON_DOC="${1:-}"
[ -f "$LESSON_DOC" ] || { echo "ERROR: lesson file not found: $LESSON_DOC"; exit 1; }

# Write content to temp file to avoid shell arg escaping issues
cp "$LESSON_DOC" /tmp/zai_quiz_lesson.txt
# Extract learning outcomes section into a separate temp file
awk '/## Learning Outcomes/,/^## /' /tmp/zai_quiz_lesson.txt | head -20 > /tmp/zai_quiz_objectives.txt
```

### Step 2 — Call GLM-5.1 + write output
```bash
OUTPUT_DIR="stages/04-quiz-recall/output"
mkdir -p "$OUTPUT_DIR"
LESSON_NAME=$(basename "$LESSON_DOC" .md)
OUTPUT_FILE="$OUTPUT_DIR/${LESSON_NAME}-quiz.json"

python3 - /tmp/zai_quiz_lesson.txt /tmp/zai_quiz_objectives.txt <<'PYEOF' > "$OUTPUT_FILE"
import os, sys, json

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

lesson_content = open(sys.argv[1]).read() if len(sys.argv) > 1 else ""
objectives = open(sys.argv[2]).read() if len(sys.argv) > 2 else ""

SYSTEM = """You write quiz questions for a GTM engineering curriculum.
Rules:
- Every question must be answerable from the lesson content — no outside knowledge required
- Questions test understanding, not memorization of wording
- 4 answer choices per question: 1 correct, 3 plausible distractors
- Include a brief explanation for the correct answer
- Distribute across: recall (30%), application (50%), analysis (20%)
Output ONLY a valid JSON array — no markdown fences, no preamble, no trailing text."""

USER = f"""Write 5 quiz questions for this lesson.

Learning objectives:
{objectives[:500]}

Lesson content:
{lesson_content[:4000]}

Output JSON:
[
  {{
    "id": "q1",
    "type": "recall|application|analysis",
    "question": "...",
    "choices": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
    "correct": "A",
    "explanation": "..."
  }}
]"""

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

### Step 3 — Validate JSON + report
```bash
BYTES=$(wc -c < "$OUTPUT_FILE" 2>/dev/null || echo 0)
if [ "$BYTES" -lt 100 ]; then
  echo "ERROR: output too small ($BYTES bytes) — likely API failure. Check $OUTPUT_FILE"
  rm -f /tmp/zai_quiz_lesson.txt /tmp/zai_quiz_objectives.txt
  exit 1
fi

# Validate JSON — if malformed, surface raw output for repair
python3 -c "
import json, sys
try:
    data = json.load(open('$OUTPUT_FILE'))
    print(f'Valid JSON: {len(data)} questions written to $OUTPUT_FILE')
except json.JSONDecodeError as e:
    print(f'WARN: JSON malformed — {e}')
    print('Raw output saved to $OUTPUT_FILE for manual repair')
    sys.exit(0)  # non-fatal — surface to Claude Code
"

# Run audit if available
python3 scripts/audit_lessons.py 2>/dev/null && echo "Audit passed" || true
rm -f /tmp/zai_quiz_lesson.txt /tmp/zai_quiz_objectives.txt
```
