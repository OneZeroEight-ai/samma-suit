# Launch Copy — For Review

All copy below is ready to post. Nothing has been posted yet.

---

## Hacker News

**Title:** Samma Suit – Eight layers of security for AI agents (open source)

**URL:** https://sammasuit.com

---

## Reddit

### r/programming

**Title:** We run 16 AI agents in production. Here's what OpenClaw gets wrong, and our open-source fix.

**Body:**
We're the team behind OneZeroEight.ai — 16 genre-specialized AI agents managing music promotion campaigns across 3,000+ playlists (48M combined reach).

When OpenClaw exploded in popularity and immediately started producing CVEs, malicious skills, and $750/mo API burns, we decided to open-source the security architecture we've been running in production.

The result is the **Samma Suit** — an 8-layer security framework for AI agent systems:

1. SUTRA — Gateway (rate limiting, origin validation, TLS)
2. DHARMA — Permissions (roles, policy engine, default-deny)
3. SANGHA — Skill Vetting
4. KARMA — Cost Controls
5. SILA — Audit Trail
6. METTA — Identity
7. BODHI — Isolation
8. NIRVANA — Recovery

Layers 1-2 are fully implemented with 60 tests passing. Layers 3-8 are stubbed with ABC base classes ready to implement.

It's a pip-installable Python package that mounts on FastAPI in ~5 lines:

```python
from samma import SammaSuit, SUTRASettings
suit = SammaSuit(app)
suit.activate_sutra(settings=SUTRASettings(...))
suit.activate_dharma()
```

MIT licensed. Python 3.10+. FastAPI native.

GitHub: https://github.com/OneZeroEight-ai/samma-suit
Site: https://sammasuit.com
Manifesto: https://sammasuit.com (docs/samma_manifesto.md in the repo)

---

### r/cybersecurity

**Title:** OpenClaw's security problems run deeper than CVE-2026-25253. We built an 8-layer alternative.

**Body:**
OpenClaw had a rough February: CVE-2026-25253 (1-click RCE via WebSocket hijack, CVSS 8.8), 341 malicious skills delivering Atomic Stealer on ClawHub, exposed Moltbook APIs, and time-shifted prompt injection via persistent memory.

These aren't bugs — they're architectural gaps. One agent, one scope, full access, no governance.

We run 16 AI agents in production at OneZeroEight.ai and just open-sourced the security framework we use: the **Samma Suit** — 8 layers that each map to a specific vulnerability class:

| Layer | Stops |
|-------|-------|
| SUTRA (Gateway) | WebSocket hijacking, origin spoofing |
| DHARMA (Permissions) | Privilege escalation, monolithic access |
| SANGHA (Skill Vetting) | Supply chain attacks, malicious skills |
| KARMA (Cost Controls) | Runaway API costs |
| SILA (Audit Trail) | Memory poisoning, invisible actions |
| METTA (Identity) | Agent spoofing |
| BODHI (Isolation) | Lateral movement, sandbox bypass |
| NIRVANA (Recovery) | No rollback, no kill switch |

MIT licensed Python package. Layers 1-2 fully implemented, 3-8 stubbed.

https://github.com/OneZeroEight-ai/samma-suit

---

### r/Python

**Title:** samma-suit: Open-source security middleware for AI agents (FastAPI, 60 tests, MIT)

**Body:**
Just released `samma-suit` — a pip-installable security framework for AI agent systems.

- 8 layers: gateway, permissions, skill vetting, cost controls, audit, identity, isolation, recovery
- Layers 1-2 fully implemented: SUTRA (Starlette middleware for rate limiting + origin validation) and DHARMA (FastAPI Depends() for role-based permissions with default-deny)
- 60 tests passing
- Mounts on FastAPI in 5 lines
- In-memory sliding window rate limiter with pluggable backend protocol
- 33 permission types, 7 default roles, policy engine with deny > grant > role > default-deny resolution

```bash
pip install samma-suit
```

```python
from samma import SammaSuit, SUTRASettings
suit = SammaSuit(app)
suit.activate_sutra(settings=SUTRASettings(
    allowed_origins=["https://yourapp.com"],
    rate_limit_per_ip=100,
))
suit.activate_dharma()
```

GitHub: https://github.com/OneZeroEight-ai/samma-suit

Built by OneZeroEight.ai — we run 16 AI agents in production managing music promotion.

---

### r/selfhosted

**Title:** Self-hosted AI agent security: 8-layer framework as an alternative to OpenClaw's approach

**Body:**
If you're self-hosting AI agents (OpenClaw or otherwise), you might want to look at the Samma Suit — an open-source security framework we just released.

It's a pip-installable Python package that adds rate limiting, origin validation, role-based permissions, and a default-deny policy engine to any FastAPI app. Layers 3-8 (skill vetting, cost controls, audit trail, identity, isolation, recovery) are stubbed and ready for community implementation.

We built it because we run 16 AI agents in production at OneZeroEight.ai and needed something that actually governs what agents can do.

- No Redis required (in-memory rate limiter, pluggable backend)
- Single-worker friendly (Railway, fly.io, etc.)
- MIT licensed

https://github.com/OneZeroEight-ai/samma-suit

---

## X/Twitter Thread (@OneZeroEight_ai)

**Tweet 1:**
OpenClaw has the right idea and the wrong architecture.

We run 16 AI agents in production. Here's what we built instead. 🧵

**Tweet 2:**
The damage report from February alone:
- CVE-2026-25253: 1-click RCE via WebSocket hijack
- 341 malicious skills on ClawHub
- $750/mo API waste from uncontrolled cron jobs
- 1.5M agents on Moltbook with zero identity verification

These aren't bugs. They're missing architecture.

**Tweet 3:**
The Samma Suit: 8 layers of security, each named for the Noble Eightfold Path.

1. SUTRA — Gateway
2. DHARMA — Permissions
3. SANGHA — Skill Vetting
4. KARMA — Cost Controls
5. SILA — Audit Trail
6. METTA — Identity
7. BODHI — Isolation
8. NIRVANA — Recovery

**Tweet 4:**
Every layer maps to a real attack class that was exploited in the OpenClaw ecosystem in the past month.

One agent with full access to everything isn't a security model. It's the absence of one.

**Tweet 5:**
It's open source. MIT licensed. Mounts on FastAPI in 5 lines.

pip install samma-suit

Layers 1-2 are fully implemented with 60 tests passing. Layers 3-8 are stubbed and ready for the community.

**Tweet 6:**
Read the full manifesto: sammasuit.com

GitHub: github.com/OneZeroEight-ai/samma-suit
Discord: discord.gg/4A6ExTnKnK

Same firepower. Built-in protection.

info@sammasuit.com

---

## Discord Announcement (discord.gg/4A6ExTnKnK)

**Channel:** #announcements

The Samma Suit SDK is now open source.

8 layers of security for AI agents — gateway, permissions, skill vetting, cost controls, audit trail, identity, isolation, and recovery. Built by the OneZeroEight team based on the architecture we use to run 16 agents in production.

Layers 1-2 (SUTRA gateway + DHARMA permissions) are fully implemented with 60 tests passing. Layers 3-8 are stubbed with ABC base classes — ready for the community to implement.

`pip install samma-suit`

**GitHub:** https://github.com/OneZeroEight-ai/samma-suit
**Site:** https://sammasuit.com
**Manifesto:** Read "We Run 16 AI Agents in Production. Here's What OpenClaw Gets Wrong." in the repo docs.

MIT licensed. Python 3.10+. FastAPI native.
