# /build-site-component

Generate site components, Helix implementation code, and student-facing UI logic.
Uses GLM-5 (strong coding + multi-step reasoning). Active from Stage 05.

## When to invoke
- Stage 05 Helix build is running
- A site component spec exists and needs implementation
- User says "build the [component]", "implement [feature] in the site"
- Helix gate logic, FSRS integration, or student state components

## Chain

### Step 0 — Pre-flight
```bash
python3 -c "import openai" 2>/dev/null || { echo "ERROR: pip install openai"; exit 1; }
[ -n "$ZHIPUAI_API_KEY" ] || { echo "ERROR: ZHIPUAI_API_KEY not set — check .env"; exit 1; }
```

### Step 1 — Read component spec + existing site patterns
```bash
SPEC="${1:-}"
[ -f "$SPEC" ] || { echo "ERROR: spec file not found: $SPEC"; exit 1; }
COMPONENT_NAME=$(basename "$SPEC" .md)

# Write context to temp files to avoid shell arg escaping issues
cp "$SPEC" /tmp/zai_comp_spec.txt

find site-new/ phases/ -name "*.js" -o -name "*.ts" -o -name "*.jsx" 2>/dev/null \
  | head -5 | xargs head -30 2>/dev/null > /tmp/zai_comp_existing.txt

cat stages/00-d-helix-design/output/*.md 2>/dev/null | head -100 > /tmp/zai_comp_helix.txt
```

### Step 2 — Call GLM-5 + write output
```bash
OUTPUT_DIR="stages/05-helix-build/output/components"
mkdir -p "$OUTPUT_DIR"
OUTPUT_FILE="$OUTPUT_DIR/${COMPONENT_NAME}.tsx"

python3 - /tmp/zai_comp_spec.txt /tmp/zai_comp_existing.txt /tmp/zai_comp_helix.txt <<'PYEOF' > "$OUTPUT_FILE"
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

spec          = open(sys.argv[1]).read() if len(sys.argv) > 1 else ""
existing      = open(sys.argv[2]).read() if len(sys.argv) > 2 else ""
helix_design  = open(sys.argv[3]).read() if len(sys.argv) > 3 else ""

SYSTEM = """You are a frontend engineer building a GTM engineering curriculum site.
You write clean, minimal, well-typed code. Follow the patterns in the existing codebase.
No unnecessary abstractions. When building Helix (student memory/FSRS) components:
keep state simple, surface review prompts clearly, handle empty/loading/error states explicitly."""

USER = f"""Build this component:

Spec:
{spec[:2000]}

Existing site patterns (for style reference):
{existing[:2000]}

Helix design context:
{helix_design[:1000]}

Output the complete implementation. Include: component file, any required types/interfaces,
brief inline comments for non-obvious logic only."""

response = client.chat.completions.create(
    model="GLM-5",
    messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": USER}],
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
if [ "$BYTES" -lt 100 ]; then
  echo "ERROR: output too small ($BYTES bytes) — likely API failure. Check $OUTPUT_FILE"
  rm -f /tmp/zai_comp_spec.txt /tmp/zai_comp_existing.txt /tmp/zai_comp_helix.txt
  exit 1
fi
echo "Written: $OUTPUT_FILE ($BYTES bytes)"
rm -f /tmp/zai_comp_spec.txt /tmp/zai_comp_existing.txt /tmp/zai_comp_helix.txt
```

### Step 4 — Review gate
Before merging any component to `site-new/`, invoke `/review` on the output file.
GLM-5 code output is good but always needs a review pass before it touches the live site.
