<!-- /autoplan restore point: /c/Users/raymo/.gstack/projects/BlueSkyGTM-blueskygtm-engineering/master-autoplan-restore-20260612-033405.md -->
# Operator-Kit Architecture Plan: GLM Proxy Skills

## Problem Statement

The 5 operator-kit skills run on Z.ai GLM models. The Z.ai API key must not live
in Claude Code's environment or the git repo. The call format (OpenAI-compatible)
is the same across all skills — only the model and system prompt change per skill.

## Approved Architecture: Proxy + Function-Named Skills

**Proxy layer** (`BlueSkyGTM/openai-proxy` on Railway):
- Accepts standard `Authorization: Bearer <PROXY_SECRET_KEY>` (OpenAI SDK compatible)
- Forwards to configurable upstream (`OPENAI_BASE_URL` env var in Railway)
- `OPENAI_API_KEY` (Z.ai key) lives only in Railway — never in this repo or Claude Code
- Swap upstream (OpenAI ↔ Z.ai) by changing one Railway env var, no code change

**Skills layer** (`skills/operator-kit/` in this repo):
- Each skill is a gstack slash command with a SKILL.md + backing Python script
- Scripts use standard `openai` Python SDK (`base_url=PROXY_URL`, `api_key=PROXY_KEY`)
- Claude Code invokes skills via `/write-lesson`, `/scan-repo`, etc. — not raw agent dispatch
- Skill names reflect the JOB, not the agent name — easier routing, clearer CLAUDE.md entries

```
Claude Code
    │
    ├── /write-lesson      → skills/operator-kit/write-lesson/
    ├── /write-quiz        →   SKILL.md + scripts/glm_call.py
    ├── /write-exercise    →   (Lyra content — GLM-5.1)
    │
    ├── /build-site-component → skills/operator-kit/build-site-component/
    │                           (Lyra code — GLM-5)
    │
    ├── /scan-repo         → skills/operator-kit/scan-repo/
    │                        (Echo — GLM-4.7-Flash)
    │
    ├── /quality-check     → skills/operator-kit/quality-check/
    │                        (Hypatia — GLM-4.7)
    │
    └── /find-citations    → skills/operator-kit/find-citations/
                             (Newton — GLM-4.5-Air)
                                │
                                ▼
                    Railway proxy (openai-proxy)
                    PROXY_URL = https://<project>.up.railway.app
                    PROXY_KEY = <shared secret>
                                │
                                ▼ Authorization: Bearer <Z.ai key>
                    Z.ai GLM endpoint
                    https://open.bigmodel.cn/api/paas/v4/
```

## Environment Variables

| Var | Where it lives | Value |
|-----|---------------|-------|
| `OPENAI_API_KEY` | Railway env only | Z.ai API key |
| `OPENAI_BASE_URL` | Railway env only | `https://open.bigmodel.cn/api/paas/v4` |
| `PROXY_SECRET_KEY` | Railway env only | Random shared secret |
| `PROXY_URL` | `.env` (this repo, gitignored) | Railway deployment URL |
| `PROXY_KEY` | `.env` (this repo, gitignored) | Same as Railway's `PROXY_SECRET_KEY` |

## Proxy Update Required

`BlueSkyGTM/openai-proxy` needs two changes before operator-kit skills can use it:
1. **Auth**: accept `Authorization: Bearer` in addition to `x-proxy-auth`
2. **Configurable upstream**: read `OPENAI_BASE_URL` env var instead of hardcoded OpenAI URL
3. **Embeddings endpoint**: add `/v1/embeddings` route (needed for gbrain Z.ai embeddings later)

Updated `index.js` ready at: `vault/proxy-index-update.js` — copy this file into
the `BlueSkyGTM/openai-proxy` repo and push, then Railway auto-deploys.

Railway env vars to set after pushing:
```
OPENAI_API_KEY     = c6f5e3a0c7f34384a329583a7b9274a7.firXV7TSgZb9QdwG
OPENAI_BASE_URL    = https://open.bigmodel.cn/api/paas/v4
PROXY_SECRET_KEY   = <generate a random string, e.g. openssl rand -hex 32>
```

Then add to `.env` in this repo:
```
PROXY_URL=https://<your-railway-project>.up.railway.app
PROXY_KEY=<same value as PROXY_SECRET_KEY>
```

## Skill File Structure

Each function-named skill follows the same pattern:

```
skills/operator-kit/<skill-name>/
├── SKILL.md          — gstack skill definition (workflow, brief injection, model)
└── run.py            — Python script: loads context, calls proxy, writes output
```

`run.py` shared pattern:
```python
import os, sys
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["PROXY_KEY"],
    base_url=os.environ["PROXY_URL"] + "/v1",
)

# model, system_prompt, and context are injected per-skill from SKILL.md brief
response = client.chat.completions.create(
    model=MODEL,          # e.g. "GLM-5.1"
    messages=[...],
    stream=True,
)
for chunk in response:
    print(chunk.choices[0].delta.content or "", end="", flush=True)
```

## Skill → Model Assignments

| Skill | Function | GLM Model | Active |
|-------|----------|-----------|--------|
| `/write-lesson` | Draft lesson docs + outlines | GLM-5.1 | Stage 01 |
| `/write-quiz` | Quiz banks (FSRS-ready) | GLM-5.1 | Stage 04 |
| `/write-exercise` | Exercise specs | GLM-5.1 | Stage 03 |
| `/build-site-component` | Site components, Helix impl | GLM-5 | Stage 05 |
| `/scan-repo` | Read-only codebase traversal | GLM-4.7-Flash | Stage 01+ |
| `/quality-check` | Curriculum audit, gap detection | GLM-4.7 | Stage 09 |
| `/find-citations` | Gap-fill research, citation finding | GLM-4.5-Air | Stage 01+ |

## Decision Audit Trail (updated)

| # | Decision | Rationale | Supersedes |
|---|----------|-----------|------------|
| 1 | Proxy architecture over direct key in env | Z.ai key lives in Railway only; rotate without touching repo | Original Option A (Anthropic format proxy) |
| 2 | Standard `openai` SDK over `zhipuai` SDK | Proxy speaks OpenAI format; no JWT handling in scripts | Decision 4 (zhipuai SDK streaming) |
| 3 | Function-named skills over agent-named scripts | Task routing via CLAUDE.md is clearer; `/write-lesson` beats `dispatch.py --agent lyra` | Original agent dispatch model |
| 4 | One `run.py` per skill, shared client pattern | Same rationale as original D9 (independent updates, no coupling) | — |
| 5 | MCP upgrade still deferred to pre-Stage 08 | Proxy + skills covers Stage 01-07 cleanly | — |
| 6 | `OPENAI_BASE_URL` in Railway, not repo | Swap Z.ai ↔ OpenAI by changing one env var; zero code change | — |

## Build Order

1. Update `BlueSkyGTM/openai-proxy` with `vault/proxy-index-update.js`
2. Set Railway env vars, get deployment URL
3. Add `PROXY_URL` + `PROXY_KEY` to `.env`
4. Scaffold `skills/operator-kit/` with shared `lib/glm_client.py` + per-skill dirs
5. Write each skill's SKILL.md brief (sourced from `stages/00-c-agent-setup/output/`)
6. Update `references/runtime-guide.md` routing declarations
7. Smoke-test each skill before Stage 01

Must complete before Stage 01.
