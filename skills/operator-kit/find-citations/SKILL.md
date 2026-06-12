# /find-citations

Gap-fill research: surfaces citation pointers and search queries for undercited claims.
Uses GLM-4.5-Air (lightweight, fast). Active from Stage 01+.

## When to invoke
- `/quality-check` flags unsupported claims or coverage gaps
- A lesson references a concept without a source
- Stage 00-b GTM content mapping needs additional citations
- User says "find a source for", "what backs this up", "citations for [topic]"

## Note on output
This skill returns **citation pointers and search queries**, not verified URLs.
GLM cannot browse the web; asking it to produce URLs produces hallucinations.
Use the output to guide manual source lookup or a browser-enabled tool.

## Chain

### Step 0 — Pre-flight
```bash
python3 -c "import openai" 2>/dev/null || { echo "ERROR: pip install openai"; exit 1; }
[ -n "$ZHIPUAI_API_KEY" ] || { echo "ERROR: ZHIPUAI_API_KEY not set — check .env"; exit 1; }
```

### Step 1 — Identify gaps
```bash
TOPIC="${1:-GTM engineering fundamentals}"
cat stages/00-b-gtm-content-mapping/output/source-citations.md 2>/dev/null \
  | grep -i "$TOPIC" | head -20 > /tmp/zai_cite_existing.txt
cat stages/09-quality-pass/output/*.md 2>/dev/null \
  | grep -A2 "Coverage Gaps" | head -30 > /tmp/zai_cite_gaps.txt
```

### Step 2 — Call GLM-4.5-Air + append to citations file
```bash
CITATIONS_FILE="stages/00-b-gtm-content-mapping/output/source-citations.md"
mkdir -p "$(dirname $CITATIONS_FILE)"
DATESTAMP=$(date +%Y-%m-%d)

python3 - "$TOPIC" /tmp/zai_cite_existing.txt /tmp/zai_cite_gaps.txt <<'PYEOF' >> "$CITATIONS_FILE"
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

topic    = sys.argv[1] if len(sys.argv) > 1 else ""
existing = open(sys.argv[2]).read() if len(sys.argv) > 2 else ""
gaps     = open(sys.argv[3]).read() if len(sys.argv) > 3 else ""

SYSTEM = """You are a research assistant for a GTM engineering curriculum.
You surface citation pointers — the right type of source, the publication to look in,
and the specific claim to search for. You do NOT produce URLs because you cannot
browse the web and invented URLs are worse than no URL.
Sources to point toward: industry blogs (a16z, Sequoia, FirstRound), vendor docs
(Salesforce, HubSpot, Segment, dbt, Fivetran), analyst reports, practitioner
newsletters (RevOps Co-op, GTM Alliance), and technical documentation."""

USER = f"""Surface 5-10 citation pointers for: {topic}

Existing citations we already have:
{existing[:1000] if existing else "None yet."}

Gaps flagged by quality audit:
{gaps[:500] if gaps else "None specified."}

For each citation pointer return:
- **[Publication / Source type]** — [specific claim to look for] | Search query: "[search terms]"

Do NOT invent URLs. Surface where to look and what to search for."""

response = client.chat.completions.create(
    model="GLM-4.5-Air",
    messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": USER}],
    max_tokens=1500,
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
BYTES=$(wc -c < "$CITATIONS_FILE" 2>/dev/null || echo 0)
if [ "$BYTES" -lt 50 ]; then
  echo "ERROR: citations file empty or too small — likely API failure"
  rm -f /tmp/zai_cite_existing.txt /tmp/zai_cite_gaps.txt
  exit 1
fi
echo "Appended citation pointers to: $CITATIONS_FILE"
echo "NOTE: these are search pointers, not verified URLs — look up the actual sources."
rm -f /tmp/zai_cite_existing.txt /tmp/zai_cite_gaps.txt
```
