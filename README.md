<p align="center">
    <img src="pulse_avatar.png" alt="Sammā Suit" width="200" height="200" style="border-radius: 50%;">
</p>

<h1 align="center">Sammā Suit</h1>
<p align="center"><em>Eight layers of Right Protection for autonomous AI agents</em></p>

<p align="center">
    <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python 3.11+">
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT">
    <img src="https://img.shields.io/badge/tests-73%20passing-brightgreen.svg" alt="Tests: 73 passing">
    <img src="https://img.shields.io/badge/layers-8%2F8%20enforced-purple.svg" alt="Layers: 8/8 enforced">
</p>

<p align="center">
    <a href="https://sammasuit.com">sammasuit.com</a> &middot;
    <a href="https://discord.gg/4A6ExTnKnK">Discord</a> &middot;
    <a href="https://x.com/OneZeroEight_ai">@OneZeroEight_ai</a>
</p>

---

## What is this?

Sammā Suit is an open-source security framework for autonomous AI agents. Rate limiting, permissions, cost controls, audit trails, identity verification, sandboxing, and recovery — out of the box.

Built by [OneZeroEight.ai](https://onezeroeight.ai), where we run 16 genre-specialized agents in production today.

## Install

```bash
pip install samma-suit
```

Also available on ClawHub: https://clawhub.ai/OneZeroEight-ai/samma-suit

## The 8 Layers

All 8 layers are enforced in v0.1. Not stubs.

| # | Layer | Function | What it does in v0.1 |
|---|-------|----------|----------------------|
| 1 | **SUTRA** | Gateway | Origin validation, rate limiting, TLS enforcement, WebSocket auth |
| 2 | **DHARMA** | Permissions | RBAC with 33 permissions, 7 roles, model whitelist, policy engine |
| 3 | **SANGHA** | Skill Vetting | Allowlist enforcement, skill registry validation, rejects unvetted skills at gateway |
| 4 | **KARMA** | Cost Controls | Per-agent budget ceiling, BYOK API keys, monthly spend tracking, blocks requests when budget exceeded |
| 5 | **SILA** | Audit Trail | Every gateway call logged, token counts, cost tracking, full layer enforcement trace |
| 6 | **METTA** | Identity | Ed25519 keypair per agent, cryptographic response signing, signature verification |
| 7 | **BODHI** | Isolation | 30-second hard timeout on LLM calls, max_tokens capped at 4096, timeout error handling |
| 8 | **NIRVANA** | Recovery | Kill switch endpoint, instant agent termination, gateway rejects all subsequent calls |

## SUTRA (Layer 1) — Gateway

- Origin validation with glob patterns (`*.yourapp.com`)
- Per-IP and per-agent sliding window rate limiting
- TLS enforcement (warn or reject non-HTTPS)
- Configurable path exclusions (`/health`, `/docs`)
- Response headers: `X-Samma-Layer`, `X-RateLimit-Remaining`

```python
from samma import SUTRASettings

settings = SUTRASettings(
    allowed_origins=["https://yourapp.com", "https://*.yourapp.com"],
    rate_limit_per_ip=100,
    rate_limit_per_agent=200,
    rate_limit_window_seconds=60,
    tls_enforce=True,
    excluded_paths=["/health", "/docs", "/openapi.json"],
)
```

## DHARMA (Layer 2) — Permissions

- 33 permission types covering file, shell, email, database, agent, admin, and more
- Default roles: `playlist`, `social`, `pr`, `curator`, `sutra`, `dharma`, `admin`
- Policy engine: explicit deny > explicit grant > role permissions > default-deny
- FastAPI `Depends()` integration and `@dharma_protected` decorator
- Per-agent overrides beyond role defaults

```python
from samma import Permission, require_permission, PolicyEngine
from fastapi import Depends

# Protect a route
@app.post("/api/agents/spawn")
async def spawn_agent(
    _perm=Depends(require_permission(Permission.AGENT_SPAWN)),
):
    ...

# Per-agent overrides
engine = suit.policy_engine
engine.grant("special-agent-1", Permission.SHELL_EXEC)
engine.deny("rogue-agent-2", Permission.EMAIL_SEND)
```

## SANGHA (Layer 3) — Skill Vetting

- Skill allowlist enforcement at the gateway level
- Every installed skill validated against the `samma_skills` registry
- Unvetted or unapproved skills block the entire gateway call
- Skills must pass vetting (`vetting_status = "approved"`) before an agent can use them
- Prevents malicious skill injection (341 malware-laden skills found on ClawHub)

## KARMA (Layer 4) — Cost Controls

- Per-agent monthly budget ceiling in USD
- **BYOK (Bring Your Own Key)** — Pro/Team customers can supply their own Anthropic API key per agent, encrypted at rest with Fernet (AES-128-CBC + HMAC-SHA256)
- Pre-call budget check — blocks requests when spend exceeds limit
- Post-call cost recording with input/output token counts
- Monthly spend tracking with automatic budget period rollover
- Prevents runaway API costs ($750/mo waste seen in uncontrolled OpenClaw agents)

## SILA (Layer 5) — Audit Trail

- Every gateway call logged with full request/response metadata
- Token counts (input, output, cache) and cost per call
- `layers_enforced` array recorded in every audit entry
- Audit log verification — SILA confirms the log was written or raises an error
- Queryable per-agent audit history via `/api/agents/{id}/audit`

## METTA (Layer 6) — Identity

- Ed25519 keypair generated per agent at creation time
- Gateway responses signed with agent's private key
- `metta_signature` and `metta_public_key` included in every response
- Clients can verify response authenticity using the public key
- Prevents agent spoofing and ensures verified communication

## BODHI (Layer 7) — Isolation

- 30-second hard timeout on all LLM API calls
- `max_tokens` hard cap at 4096 regardless of request
- Timeout errors return `504` with `BODHI: LLM call timed out` message
- Prevents rogue processes from consuming unlimited compute
- Caps applied after DHARMA model whitelist, before the API call

## NIRVANA (Layer 8) — Recovery

- Kill switch endpoint: `POST /api/agents/{id}/kill`
- Instantly sets agent status to `terminated`
- Gateway rejects all subsequent calls for terminated agents
- Kill action logged to audit trail with `layer: NIRVANA` metadata
- Checked at router level before any gateway processing begins

## Quickstart

### 1. Install and configure

```bash
git clone https://github.com/OneZeroEight-ai/onezeroeight-backend.git
cd onezeroeight-backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set ANTHROPIC_API_KEY in .env
```

### 2. Start the server

```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Create a customer and get an API key

```bash
curl -X POST http://localhost:8000/api/billing/checkout \
  -H "Content-Type: application/json" \
  -d '{"tier": "pro", "email": "you@example.com"}'
```

Response includes your API key:
```json
{
  "checkout_url": "https://checkout.stripe.com/...",
  "customer_id": "abc-123",
  "api_key": "samma_your_key_here"
}
```

### 4. Create an agent

```bash
curl -X POST http://localhost:8000/api/agents \
  -H "Authorization: Bearer samma_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Agent", "monthly_budget_usd": 5.0, "llm_api_key": "sk-ant-..."}'
```

### 5. Send a request through the gateway

```bash
curl -X POST http://localhost:8000/api/agents/AGENT_ID/gateway \
  -H "Authorization: Bearer samma_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello"}],
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 1024
  }'
```

The response includes all 8 layers enforced:
```json
{
  "content": [{"type": "text", "text": "Hello!"}],
  "metta_signature": "a1b2c3...",
  "metta_public_key": "d4e5f6...",
  "layers_enforced": ["SUTRA", "NIRVANA", "SANGHA", "KARMA", "DHARMA", "BODHI", "METTA", "SILA"]
}
```

### 6. Verify the audit log

```bash
curl http://localhost:8000/api/agents/AGENT_ID/audit \
  -H "Authorization: Bearer samma_your_key_here"
```

Every call is logged with token counts, cost, and which layers were enforced.

## SDK Usage

```python
from fastapi import FastAPI, Depends
from samma import SammaSuit, SUTRASettings, Permission, require_permission

app = FastAPI()

# One-call setup
suit = SammaSuit(app)
suit.activate_sutra(settings=SUTRASettings(
    allowed_origins=["https://yourapp.com"],
    rate_limit_per_ip=100,
    rate_limit_window_seconds=60,
))
suit.activate_dharma()

# Protect endpoints
@app.get("/api/admin")
async def admin_endpoint(
    _perm=Depends(require_permission(Permission.ADMIN_WRITE)),
):
    return {"access": "granted"}

# Status dashboard
@app.get("/samma/status")
async def status():
    return suit.status()
```

## Architecture

```
Request
  |
  v
SUTRA (middleware) ── rate limit, origin check, TLS
  |
  v
Router ── NIRVANA check: is agent active?
  |
  v
SANGHA ── are all installed skills vetted?
  |
  v
KARMA ── is the agent under budget?
  |
  v
DHARMA ── is this model allowed? cap max_tokens
  |
  v
BODHI ── hard cap 4096 tokens, 30s timeout
  |
  v
[LLM API Call]
  |
  v
METTA ── sign response with Ed25519 key
  |
  v
KARMA ── record cost to agent spend
  |
  v
SILA ── verify audit log written, record layers_enforced
  |
  v
Response (with signature + layer metadata)
```

All 8 layers run on every gateway call. SUTRA at the middleware level, NIRVANA at the router level, the remaining 6 inside the gateway function.

## Testing

```bash
# Run Sammā Suit SDK tests (60 tests)
cd samma && python -m pytest tests/ -v --no-cov --ignore=tests/test_layers_enforcement.py

# Run layer enforcement tests (13 tests) — from project root
python -m pytest samma/tests/test_layers_enforcement.py -v --no-cov

# All 73 tests passing
```

## FAQ

**Are all 8 layers real?**
Yes. All enforced in v0.1 with 73 passing tests. Not stubs. Every gateway call runs through all 8 layers and returns `layers_enforced` in the response.

**What attacks does this stop?**
Malicious skill injection (SANGHA), runaway costs (KARMA), unverified agents (METTA), rogue processes (BODHI), no emergency stop (NIRVANA). Each layer maps to a real vulnerability class exploited in the OpenClaw ecosystem.

**What LLMs are supported?**
Any provider. The default gateway proxies to Anthropic Claude. Swap the LLM call in `app/services/samma_gateway.py` for OpenAI, local models, or anything else.

**Is this production ready?**
v0.1 is minimally enforced. Production-hardened versions with deeper enforcement shipping Q1-Q2 2026. We run 16 agents in production at OneZeroEight.ai today.

**What about the hosted platform?**
Waitlist open. Data will be stored in Iceland (GDPR jurisdiction, geothermal powered, outside US CLOUD Act reach). Email info@sammasuit.com.

**How is this different from guardrails/rebuff/other tools?**
Those protect the LLM. Sammā Suit protects the agent — the identity, the budget, the skills, the audit trail, and the kill switch. Different layer of the stack.

**What's with the Buddhist naming?**
Sammā means "right" in Pali (as in Right Action, Right Livelihood). The 8 layers map to the Noble Eightfold Path. Built by OneZeroEight.ai — 108 is sacred in Buddhist tradition.

## Cheatsheet

Every endpoint, layer, shortcut, and config — one page.

![Sammā Suit Mega Cheatsheet](docs/images/samma-suit-cheatsheet.png)

[Download PNG](docs/images/samma-suit-cheatsheet.png) · [Interactive version](https://sammasuit.com/cheatsheet.html)

## Links

- **Product site:** [sammasuit.com](https://sammasuit.com)
- **Parent company:** [onezeroeight.ai](https://onezeroeight.ai)
- **Discord:** [discord.gg/4A6ExTnKnK](https://discord.gg/4A6ExTnKnK)
- **Twitter/X:** [@OneZeroEight_ai](https://x.com/OneZeroEight_ai)
- **Email:** info@sammasuit.com

## License

MIT — see [LICENSE](LICENSE).

---

Built by [OneZeroEight.ai](https://onezeroeight.ai) — 16 agents in production, 3,000+ verified playlists, 48M+ combined follower reach.
