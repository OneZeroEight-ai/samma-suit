# DOORMAN / Sammā Suit — Domain & Identity Strategy

> IP playbook for locking down digital real estate across domains, social handles, and brand positioning

---

## Research Findings

### Domain Landscape

| Domain | Status | Owner/Use | Risk Level |
|--------|--------|-----------|------------|
| **doorman.ai** | FOR SALE | Listed on Spaceship/Dan.com, make-an-offer | ⚠️ Premium price likely |
| **doorman.dev** | TAKEN | Active open-source Python API gateway (apidoorman/doorman on GitHub) | 🔴 Direct competitor namespace |
| **doorman.co** | TAKEN | Defunct package delivery startup (shut down 2017, Shark Tank S6). Site still live but company dead | 🟡 Dead company, domain may be acquirable |
| **getdoorman.com** | TAKEN | New Brooklyn package delivery pilot ($99/mo), active as of Dec 2025 | 🔴 Active business |
| **doorman.com** | TAKEN | Virtual Doorman® — physical building security, 400+ buildings | 🔴 Established brand |
| **sammasuit.com** | ✅ ACQUIRED | You control this | ✅ |
| **samma.ai** | UNKNOWN | No results found | 🟢 Check and register |
| **sutra.team** | OWNED | You control this | ✅ |
| **sutra.exchange** | OWNED | You control this | ✅ |
| **onezeroeight.ai** | OWNED | Your music platform | ✅ |

### Social Handle Landscape

| Handle | Platform | Status | Notes |
|--------|----------|--------|-------|
| **@doormanhq** | Instagram | TAKEN | 225 followers, 74 posts — small account |
| **@doorman** | X/Twitter | TAKEN | Was used by defunct doorman.co |
| **@OneZeroEight_ai** | X | OWNED | Your current account |
| **@sammas_offiziell** | Instagram | TAKEN | Austrian jazz band, 864 followers — irrelevant |

### Key Conflicts

1. **doorman.dev** — An active open-source API gateway project called "Doorman" doing auth, routing, rate limiting. Pre-release, Apache-2.0 licensed. GitHub: apidoorman/doorman. This is the closest competitor in namespace — same name, same general category (API security).

2. **doorman.co / doorman.com** — Physical package delivery and building security. Different industries entirely. No AI/software conflict.

3. **PyPI "doorman" package** — Registered since 2022 by a different developer. Minor concern for Python ecosystem visibility.

---

## Recommended Domain Strategy

### Tier 1: Register Immediately (Today)

These are likely available and should be locked down before anyone else reads your manifesto:

| Domain | Purpose | Estimated Cost | Registrar |
|--------|---------|---------------|-----------|
| **sammasuit.com** | Sammā Suit architecture brand | ~$12/yr | Cloudflare |
| **sammasuit.ai** | Sammā Suit AI-specific | ~$80/yr | Cloudflare |
| **doormanai.com** | DOORMAN product (avoids doorman.dev conflict) | ~$12/yr | Cloudflare |
| **doorman.security** | Perfect TLD for the product | ~$30/yr | Cloudflare |
| **samma.ai** | Short, premium Sammā brand | ~$80/yr | Cloudflare |
| **sammasuit.dev** | Developer docs / SDK | ~$12/yr | Cloudflare |

**Total: ~$225/year for the full defensive portfolio**

### Tier 2: Negotiate (This Week)

| Domain | Status | Strategy | Budget Range |
|--------|--------|----------|-------------|
| **doorman.ai** | For sale on Spaceship | Make a low offer ($500–1,500). Premium .ai domains go for $2K–$10K+ but this isn't a one-word category-killer like "agent.ai" | $500–$5,000 |

### Tier 3: Don't Bother

| Domain | Why Skip |
|--------|----------|
| doorman.dev | Active competing project — buying would be hostile and they're open-source |
| doorman.com | Virtual Doorman® is a registered trademark holder with 400+ buildings |
| doorman.co | Defunct but site still live; may be in domain limbo |
| getdoorman.com | Active Brooklyn startup pilot |

---

## Recommended URL Architecture

### Primary Setup

```
sammasuit.com            → DOORMAN / Sammā Suit primary product site
onezeroeight.ai          → Parent company + music platform
onezeroeight.ai/doorman  → Redirects to sammasuit.com
sutra.exchange           → Token portal (buy, stake, dashboard)  
sutra.team               → Internal agent dashboard / team portal
```

### If You Also Acquire doorman.ai

```
sammasuit.com            → Primary (keep as canonical)
doorman.ai               → Redirects to sammasuit.com
onezeroeight.ai          → Parent company + music platform
sutra.exchange           → Token portal
sutra.team               → Agent team dashboard
```

---

## Social Identity System

### Platform Strategy

| Platform | Handle | Purpose | Content |
|----------|--------|---------|---------|
| **X** | @OneZeroEight_ai | Parent brand (keep) | Company news, music platform, culture |
| **X** | @doorman_sec | DOORMAN product | Security advisories, OpenClaw commentary, launches |
| **X** | @sammasuit | Sammā Suit framework | Technical threads, CVE analyses, architecture posts |
| **Instagram** | @onezeroeight.ai | Keep existing | Music platform visual content |
| **Instagram** | @sammasuit | New — framework brand | Mascot content, architecture infographics, that meditating armor image |
| **Instagram** | @doorman.sec | New — product brand | Security content, product screenshots, demos |
| **Discord** | Keep existing server | Add DOORMAN channels | #doorman-general, #samma-suit-dev, #security-feed, #sutra-token |
| **GitHub** | onezeroeight/doorman | Primary repo | Open-source Sammā Suit SDK |
| **GitHub** | onezeroeight/samma-suit | Framework repo | Eight-layer reference implementation |

### Handle Priority Order (Register These Now)

**X (Twitter):**
1. @doorman_sec ← best available, "sec" = security
2. @sammasuit ← framework brand  
3. @DoormanArmor ← backup
4. @doorman_ai ← may be taken, check

**Instagram:**
1. @sammasuit ← likely available, unique
2. @doorman.sec ← product
3. @doorman.armor ← backup
4. @samma.suit ← variation

**GitHub:**
1. Create org: `doorman-sec` or `sammasuit`
2. Reserve repos: `doorman`, `samma-suit`, `samma-sdk`

---

## Brand Architecture (Both Paths Compared)

### Path A: OneZeroEight Leads

```
                    ┌─────────────────────┐
                    │   ONEZEROEIGHT.AI    │
                    │   (Parent Brand)     │
                    └─────────┬───────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
     ┌────────▼──────┐ ┌─────▼──────┐ ┌──────▼───────┐
     │   Music       │ │  DOORMAN   │ │    SUTRA     │
     │   Platform    │ │  Security  │ │    Token     │
     │              │ │  Platform  │ │              │
     │  16 Genre    │ │            │ │  sutra.team  │
     │  Agents      │ │  Sammā     │ │  sutra.      │
     │              │ │  Suit      │ │  exchange    │
     └──────────────┘ └────────────┘ └──────────────┘

Strengths:
+ Unified brand story
+ Music credibility backs security pitch
+ One Discord, one community
+ Simpler to manage

Weaknesses:
- "Music company does security" may confuse
- Limits DOORMAN growth ceiling
- Investors may see unfocused vision
```

### Path B: DOORMAN Leads

```
     ┌──────────────────────────────────────────┐
     │              DOORMAN                      │
     │     "AI Agent Security Platform"          │
     │     Powered by the Sammā Suit             │
     │                                           │
     │     "Built by the team behind             │
     │      OneZeroEight — 16 agents in          │
     │      production since 2024"               │
     └────────────────┬─────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
  ┌─────▼────┐  ┌─────▼────┐  ┌────▼─────┐
  │ Sammā    │  │  SUTRA   │  │ OneZero  │
  │ Suit SDK │  │  Token   │  │ Eight    │
  │ (OSS)    │  │          │  │ (Music)  │
  └──────────┘  └──────────┘  └──────────┘

Strengths:
+ DOORMAN stands alone in the security market
+ VC-friendly — clear product, clear market
+ OneZeroEight becomes proof point, not baggage
+ Can sell/spin DOORMAN independently

Weaknesses:
- Two brands to build simultaneously
- Two social presences to maintain
- More domains/handles to manage
```

### Recommended: Path A Now, Path B When Ready

Start with OneZeroEight as parent. Add `/doorman` to the existing site. Build traction. When DOORMAN has its own user base, split it out to its own domain. This is how Stripe started under Y Combinator, how Slack started inside Tiny Speck, how Discord started as a gaming chat tool.

**Trigger to split:** When DOORMAN gets its first 100 paying users or first press mention independent of the music platform.

---

## Immediate Action Checklist

### TODAY (30 minutes)

- [x] Register **sammasuit.com** ✅ DONE
- [ ] Register **sammasuit.ai** via Cloudflare (~$80)
- [ ] Register **doormanai.com** via Cloudflare ($12)
- [ ] Register **doorman.security** via Cloudflare (~$30)
- [ ] Register **samma.ai** via Cloudflare (~$80)
- [ ] Register **sammasuit.dev** via Cloudflare ($12)
- [ ] Create X account: **@sammasuit**
- [ ] Create X account: **@doorman_sec**
- [ ] Create Instagram: **@sammasuit**
- [ ] Create GitHub org: **sammasuit** or **doorman-sec**

### THIS WEEK

- [ ] Point sammasuit.com → landing page (doorman_landing.html)
- [ ] Make offer on **doorman.ai** via Spaceship ($500 opening offer)
- [ ] Point doormanai.com → redirect to onezeroeight.ai/doorman
- [ ] Add #doorman channel to existing Discord
- [ ] Set up sutra.exchange landing page (token dashboard)
- [ ] Set up sutra.team landing page (agent team dashboard)

### THIS MONTH

- [ ] Build onezeroeight.ai/doorman product page
- [ ] Publish Sammā Suit SDK on GitHub (sammasuit/samma-suit)
- [ ] Launch @sammasuit X account with architecture thread
- [ ] Post mascot image (meditating armor) to Instagram
- [ ] If doorman.ai acquired → migrate primary product URL

---

## Domain Cost Summary

| Domain | Annual Cost | Priority |
|--------|-----------|----------|
| sammasuit.com | ~$12 | 🔴 NOW |
| sammasuit.ai | ~$80 | 🔴 NOW |
| doormanai.com | ~$12 | 🔴 NOW |
| doorman.security | ~$30 | 🔴 NOW |
| samma.ai | ~$80 | 🟡 NOW |
| sammasuit.dev | ~$12 | 🟡 NOW |
| doorman.ai | $500–$5,000 | 🟡 NEGOTIATE |
| **Total Year 1** | **~$730–$5,230** | |

---

## Key Insight

The **Sammā Suit** is actually your strongest IP to lock down right now. "Doorman" is generic and contested across multiple industries. "Sammā Suit" is unique — zero conflicts, instantly registrable, and the Pali diacritical mark makes it even more distinctive. If you can only do one thing today, register the sammasuit domains. DOORMAN can live under onezeroeight.ai/doorman until you have the premium domain secured.

---

*Prepared February 2026 · OneZeroEight.ai*
