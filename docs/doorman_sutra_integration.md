# SUTRA Token Integration Spec — DOORMAN (Sammā Suit)

> How the SUTRA token economy extends from music promotion into agent governance via the Sammā Suit

---

## Overview

DOORMAN, powered by the **Sammā Suit** (eight layers of Right Protection), introduces new utility for the SUTRA token (Polygon, contract `0x0b3f81d3e1fa01e911a8b4e49048eea0ddf2a896`) by integrating it as the native payment and incentive layer for the agent governance platform.

**Current SUTRA Utility (Music Platform):**
- Curator rewards: 50 SUTRA per honest placement
- Agent earnings: 10 SUTRA per successful outcome
- Artist payments: 20% discount vs USD
- Holder benefits: discounts for token holders

**New SUTRA Utility (Doorman):**
- Subscription payments with 20% discount
- Skill developer rewards for vetted marketplace contributions
- Agent staking for identity verification
- Governance voting on platform policies
- Bounties for security researchers

---

## Token Flows

### 1. Subscription Payments

Users can pay for Doorman Pro, Team, and Enterprise tiers in SUTRA at a 20% discount.

```
PAYMENT FLOW
─────────────────────────────────────────────
User wallet (Polygon)
  │
  ├─── SUTRA transfer ──→ Doorman Treasury
  │                         │
  │                         ├── 70% → Operations reserve
  │                         ├── 20% → Skill developer rewards pool
  │                         └── 10% → Security bounty pool
  │
  └─── Subscription activated on-chain
       (NFT receipt / access token)
```

**Pricing in SUTRA:**

| Tier | USD Price | SUTRA Price (20% discount) | SUTRA Equivalent* |
|------|-----------|---------------------------|-------------------|
| Pro | $29/mo | $23.20/mo equivalent | Variable based on market rate |
| Team | $99/mo | $79.20/mo equivalent | Variable based on market rate |
| Enterprise | Custom | Custom with SUTRA discount | Negotiated |

*SUTRA amount calculated at time of payment using SushiSwap TWAP (time-weighted average price) over 24 hours to prevent manipulation.*

### 2. Skill Developer Rewards

Developers who publish vetted skills to the Doorman marketplace earn SUTRA.

```
SKILL REWARD FLOW
─────────────────────────────────────────────
Developer submits skill
  │
  ├─── SANGHA layer: automated scan
  ├─── SANGHA layer: sandbox evaluation
  ├─── SANGHA layer: manual review (if flagged)
  │
  ├─── APPROVED ──→ Listed on marketplace
  │                   │
  │                   ├── One-time listing reward: 50 SUTRA
  │                   └── Usage rewards: 5 SUTRA per 100 installs
  │
  └─── REJECTED ──→ Feedback provided, resubmission allowed
```

**Monthly Skill Developer Pool:** 20% of SUTRA subscription revenue, distributed proportionally by install count.

### 3. Agent Identity Staking (METTA Layer)

To create a verified agent identity on Doorman, users stake a small amount of SUTRA. This creates economic cost for identity spam/spoofing.

```
IDENTITY STAKING
─────────────────────────────────────────────
User creates agent
  │
  ├─── Stake 100 SUTRA ──→ Staking contract
  │                          │
  │                          ├── Agent receives verified badge
  │                          ├── Stake locked for 30 days minimum
  │                          └── Slash conditions:
  │                               ├── Agent flagged as malicious → 100% slash
  │                               ├── Agent violates policies → 50% slash
  │                               └── Clean record → full unstake after 30 days
  │
  └─── Agent identity minted (on-chain attestation)
```

**Why staking works here:** OpenClaw/Moltbook showed that 17,000 humans created 1.5M agents with zero friction. Requiring a 100 SUTRA stake per agent identity creates meaningful economic cost for spam while remaining accessible for legitimate users.

### 4. Governance Voting

SUTRA holders can vote on Doorman platform policies:

- **Skill marketplace policies** — what categories of skills are permitted
- **Default permission templates** — which DHARMA permission sets ship as defaults
- **Cost control thresholds** — default KARMA budget caps for new instances
- **Security response priorities** — how the team allocates security bounty resources

```
GOVERNANCE FLOW
─────────────────────────────────────────────
Proposal submitted (minimum 10,000 SUTRA to propose)
  │
  ├─── 7-day discussion period
  ├─── 7-day voting period (1 SUTRA = 1 vote, quadratic optional)
  │
  ├─── PASSED (>50% + quorum of 5% supply) ──→ Implementation
  └─── FAILED ──→ Archive, can resubmit after 30 days
```

### 5. Security Bounties

The NIRVANA recovery layer is funded partly by SUTRA bounties for security researchers.

```
BOUNTY TIERS
─────────────────────────────────────────────
Critical (RCE, data exfiltration)    → 10,000 SUTRA
High (privilege escalation, bypass)  →  5,000 SUTRA
Medium (information disclosure)      →  2,000 SUTRA
Low (minor, theoretical)             →    500 SUTRA

Pool: 10% of SUTRA subscription revenue + dedicated allocation
```

---

## Smart Contract Architecture

### Contracts Required

```
DOORMAN CONTRACTS (Polygon)
─────────────────────────────────────────────

1. DoormanSubscription.sol
   - Accepts SUTRA payments for subscriptions
   - Calculates SUTRA price using SushiSwap TWAP oracle
   - Mints subscription NFT (access token)
   - Handles renewals and cancellations
   - Distributes to treasury splits (70/20/10)

2. DoormanStaking.sol
   - Accepts SUTRA stakes for agent identity
   - Manages lock periods (30-day minimum)
   - Implements slash conditions
   - Emits identity attestation events

3. DoormanRewards.sol
   - Manages skill developer reward pool
   - Tracks install counts (off-chain oracle)
   - Distributes monthly rewards proportionally
   - Handles one-time listing rewards

4. DoormanGovernance.sol
   - Proposal creation (10,000 SUTRA minimum)
   - Voting (snapshot-based, 1 token = 1 vote)
   - Quorum checking (5% of circulating supply)
   - Execution queue with timelock

5. DoormanBounty.sol
   - Bounty pool management
   - Payout approval (multisig: 3-of-5 team members)
   - Tier-based reward distribution
```

### Integration with Existing SUTRA Contract

The existing SUTRA token contract (`0x0b3f...a896`) remains unchanged. Doorman contracts interact with it via standard ERC-20 `approve` + `transferFrom` patterns.

```
EXISTING                    NEW
────────                    ───
SUTRA Token (ERC-20)  ←──→  DoormanSubscription
         on Polygon   ←──→  DoormanStaking
                      ←──→  DoormanRewards
                      ←──→  DoormanGovernance
                      ←──→  DoormanBounty
                      
SushiSwap Pool  ──────────→  Price Oracle (TWAP)
```

---

## Token Economics Impact

### Supply Allocation for Doorman

From the existing 108,000,000 SUTRA total supply:

| Allocation | Amount | Purpose |
|-----------|--------|---------|
| Skill Developer Rewards | 5,000,000 SUTRA | 3-year vesting for marketplace incentives |
| Security Bounty Pool | 2,000,000 SUTRA | Ongoing security researcher rewards |
| Early Adopter Airdrop | 1,000,000 SUTRA | First 1,000 Doorman Pro subscribers |
| Governance Bootstrap | 500,000 SUTRA | Initial governance proposal funding |
| **Total Doorman Allocation** | **8,500,000 SUTRA** | **~7.9% of total supply** |

### Demand Drivers

Doorman creates new SUTRA demand through:

1. **Subscription payments** — recurring buy pressure from Pro/Team/Enterprise users paying in SUTRA for the 20% discount
2. **Identity staking** — SUTRA locked in staking contracts (removed from circulating supply)
3. **Governance participation** — holding SUTRA to vote on platform policies
4. **Developer rewards** — developers holding SUTRA earned from marketplace contributions

### Projected Impact (Conservative)

| Metric | Month 1 | Month 6 | Month 12 |
|--------|---------|---------|----------|
| Doorman Pro subscribers | 100 | 1,000 | 5,000 |
| SUTRA subscribers (50% uptake) | 50 | 500 | 2,500 |
| Monthly SUTRA subscription revenue | ~$1,160 equiv | ~$11,600 equiv | ~$58,000 equiv |
| Staked agents (100 SUTRA each) | 200 | 3,000 | 20,000 |
| SUTRA locked in staking | 20,000 | 300,000 | 2,000,000 |
| Active skill developers | 10 | 100 | 500 |

---

## Implementation Phases

### Phase 1: Subscription Payments (Launch)
- Deploy DoormanSubscription.sol
- Integrate SushiSwap TWAP oracle for pricing
- Add SUTRA payment option to Doorman checkout
- Mint subscription NFTs as access tokens

### Phase 2: Identity Staking (Month 2)
- Deploy DoormanStaking.sol
- Integrate with METTA identity layer
- Verified badge system for staked agents
- Slash condition monitoring

### Phase 3: Skill Rewards (Month 3)
- Deploy DoormanRewards.sol
- Off-chain oracle for install count tracking
- Monthly distribution automation
- Developer dashboard for earnings tracking

### Phase 4: Governance (Month 4)
- Deploy DoormanGovernance.sol
- Initial proposals for community input
- Voting interface in Doorman dashboard
- Timelock execution for passed proposals

### Phase 5: Security Bounties (Month 5)
- Deploy DoormanBounty.sol
- Public bounty program announcement
- Integration with existing security research community
- Multisig payout approval process

---

## Flywheel Effect

```
More Doorman users
       │
       ▼
More SUTRA demand (subscriptions, staking)
       │
       ▼
Higher SUTRA value
       │
       ▼
More attractive skill developer rewards
       │
       ▼
Better skill marketplace
       │
       ▼
More Doorman users ←──── (cycle repeats)
       │
       ▼
More security bounty funding
       │
       ▼
Better security posture
       │
       ▼
Enterprise trust → Enterprise subscriptions → More SUTRA demand
```

---

## Risk Considerations

| Risk | Mitigation |
|------|-----------|
| SUTRA price volatility affecting subscription pricing | 24-hour TWAP oracle smooths short-term manipulation; users can also pay in USD |
| Low initial SUTRA liquidity on SushiSwap | Phase 1 focuses on USD payments; SUTRA option is a bonus, not a requirement |
| Regulatory classification of staking | Legal review before launch; staking is for identity verification (utility), not yield |
| Smart contract vulnerabilities | Professional audit before mainnet deployment; bug bounty program from day one |
| Token concentration enabling governance capture | Quadratic voting option; proposal quorum requirements; team retains veto for first 12 months |

---

## Summary

DOORMAN's Sammā Suit extends SUTRA from a music-industry token into a general-purpose agent governance token. Every interaction with the Doorman platform — subscribing, staking identities, publishing skills, voting on policies, reporting vulnerabilities — creates a SUTRA transaction. The token becomes the connective tissue between security, incentives, and governance.

The music platform proved the model: agents earn for outcomes, not activity. Doorman scales that model to the entire AI agent ecosystem.

---

*Contract: 0x0b3f81d3e1fa01e911a8b4e49048eea0ddf2a896 · Network: Polygon · DEX: SushiSwap*
*sammasuit.com · onezeroeight.ai · support@onezeroeight.ai · @OneZeroEight_ai*
