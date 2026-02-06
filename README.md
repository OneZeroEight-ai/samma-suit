# Samma Suit SDK

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests: 60 passing](https://img.shields.io/badge/tests-60%20passing-brightgreen)]()

**Eight layers of Right Protection for autonomous AI agents.**

The Samma Suit (Pali: *Samma* — "right, proper") is an open-source security framework that gives AI agent systems rate limiting, permissions, cost controls, audit trails, identity verification, sandboxing, and recovery — out of the box.

[sammasuit.com](https://sammasuit.com) | [Discord](https://discord.gg/4A6ExTnKnK) | [Docs](docs/)

## Install

```bash
pip install samma-suit
```

## Quickstart

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

See [`examples/fastapi_demo.py`](examples/fastapi_demo.py) for a complete runnable demo.

## The Eight Layers

| # | Layer | Function | Status |
|---|-------|----------|--------|
| 1 | **SUTRA** | Gateway — rate limiting, origin validation, TLS | Active |
| 2 | **DHARMA** | Permissions — roles, policy engine, default-deny | Active |
| 3 | **SANGHA** | Skill Vetting — scan, sandbox, approve skills | Stub |
| 4 | **KARMA** | Cost Controls — per-agent budgets, spend tracking | Stub |
| 5 | **SILA** | Audit Trail — event logging, anomaly detection | Stub |
| 6 | **METTA** | Identity — cryptographic agent signing | Stub |
| 7 | **BODHI** | Isolation — process sandboxing, egress control | Stub |
| 8 | **NIRVANA** | Recovery — state snapshots, rollback, kill switches | Stub |

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

## Development

```bash
pip install -e ".[fastapi,dev]"
python -m pytest tests/ -v --no-cov
```

## License

MIT — see [LICENSE](LICENSE).

Built by [OneZeroEight.ai](https://onezeroeight.ai)
