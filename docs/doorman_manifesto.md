# We Run 16 AI Agents in Production. Here's What OpenClaw Gets Wrong.

*By the OneZeroEight team · February 2026*

> The Samma Suit is now open source → [github.com/OneZeroEight-ai/samma-suit](https://github.com/OneZeroEight-ai/samma-suit)
> info@sammasuit.com | [sammasuit.com](https://sammasuit.com)

---

OpenClaw is the most exciting thing to happen to AI agents since ChatGPT made the world care about large language models. In three months it went from a side project called Clawdbot to 100,000+ GitHub stars, 1.5 million autonomous agents on Moltbook, and mainstream coverage from Gartner to China's Ministry of Industry and Information Technology.

We're fans. We get it. The pitch is irresistible: a self-hosted AI assistant that reads your messages, manages your calendar, writes code, controls your smart home, and learns over time. It's Jarvis. It's Her. It's the thing every developer has wanted since they first touched an API.

But we also run 16 AI agents in production — every day, across 3,000+ playlists, reaching 48 million followers. Our agents have names, personalities, defined roles, and strict rules about what they can and cannot do. They earn tokens only when they deliver results. They've been operating this way since before OpenClaw existed.

And from that vantage point, we need to say something clearly:

**OpenClaw has the right idea and the wrong architecture.**

Here's what we mean.

---

## The Power Is Real

Let's give credit where it's due. OpenClaw nailed the core insight: people don't want another chatbot in a browser tab. They want an agent that lives in their messaging apps, has memory, takes initiative, and actually does things.

The feature set is genuinely impressive. Multi-channel messaging across WhatsApp, Telegram, Discord, Slack, and Signal. Persistent memory stored as local Markdown. A heartbeat system that lets agents act proactively. An extensible skill ecosystem. Browser automation. File and shell access. Model agnosticism.

This is the right product for this moment. The demand is undeniable.

The security posture, however, is not a product. It's an afterthought.

---

## The Damage Report

In the first week of February 2026 — one week — the OpenClaw ecosystem produced the following:

**CVE-2026-25253 (CVSS 8.8):** A one-click remote code execution vulnerability. The Control UI trusted `gatewayUrl` from the query string without validation and auto-connected on load, sending the stored gateway token in the WebSocket connect payload. Clicking a single malicious link gave an attacker operator-level access to your gateway. They could disable your sandbox, modify your config, and execute arbitrary code. The vulnerability worked even on instances configured to listen on loopback only.

**341 Malicious Skills on ClawHub:** Koi Security audited 2,857 skills and found 341 were malicious. 335 delivered Atomic Stealer malware disguised as crypto trading tools. They stole exchange API keys, wallet private keys, SSH credentials, and browser passwords. The barrier to uploading a skill: a GitHub account one week old.

**$20/Night API Burns:** A heartbeat cron job checking the time every 30 minutes sent approximately 120,000 tokens of context per check — costing $0.75 each. An overnight run of 25 checks cost nearly $20. Extrapolated to a month of just running reminders: $750. No budget caps. No throttling. No alerts.

**Moltbook Database Exposure:** The social network built for OpenClaw agents had its backend database wide open. Wiz researchers found exposed APIs that would allow anyone to take control of agents posting on the network. Behind 1.5 million agents: just 17,000 humans. And every post on Moltbook can act as a prompt injection against visiting agents.

**Memory Poisoning:** Koi Security identified that OpenClaw's persistent memory, combined with its tool access and autonomous execution, creates what they called "time-shifted prompt injection" — malicious payloads fragmented across sessions that appear benign individually but assemble into executable instructions when conditions align. Logic bombs for AI agents.

Laurie Voss, the founding CTO of npm, summarized it with admirable precision: "OpenClaw is a security dumpster fire."

Gartner said it "comes with unacceptable cybersecurity risk." China's National Vulnerability Database issued a formal advisory. Microsoft's security team flagged it internally. Token Security estimated 22% of their enterprise customers already had employees running OpenClaw.

This is not a fixable-with-patches problem. This is an architectural problem.

---

## Architecture Is Destiny

Here's the thing about OpenClaw's vulnerabilities: they're not bugs. They're features, taken to their logical conclusion without governance.

OpenClaw gives one agent full access to everything. That's the product. The agent that reads your email is the same agent that runs shell commands. The agent that manages your calendar is the same agent that browses the web. There is one identity, one permission set, one scope — and it's "all."

That's not a security model. That's the absence of one.

Consider how we run agents at OneZeroEight:

- **Pulse** handles Electronic/EDM. It can pitch curators, analyze tracks, and communicate in its signature high-energy style. It cannot access artist payment information, modify system configs, or communicate as another agent.
- **Velvet** handles R&B/Soul. Same constraints, different genre, different personality, different communication templates. Velvet literally cannot do what Pulse does, and vice versa.
- **SUTRA** is the office manager. It routes messages, sends welcomes, and resolves support tickets. It cannot pitch curators, analyze tracks, or modify agent configurations.

Each agent has a name, a visual identity, a defined scope, and earns tokens only for successful outcomes within that scope. This isn't theoretical. It's running right now, managing real campaigns, touching real curator relationships, moving real tokens on Polygon.

OpenClaw's architecture makes this impossible. One agent, one scope, full access. The "sandbox" is optional and bypassable (as CVE-2026-25253 proved). The skill marketplace is open and unvetted. The memory system has no integrity checking. The cost model is "hope your cron job doesn't go haywire."

You can patch individual CVEs. You cannot patch an architecture that was designed without governance.

---

## The Eight Layers OpenClaw Is Missing

We've spent the last week mapping every OpenClaw vulnerability to a specific architectural gap. The result is what we're calling the **Sammā Suit** — eight layers of Right Protection, named for the Pali word at the heart of the Noble Eightfold Path. A governance framework that, had it existed in OpenClaw from the start, would have prevented every incident listed above.

| Layer | Name | What It Protects Against |
|-------|------|------------------------|
| 1 | **SUTRA** — Gateway | Unvalidated connections, WebSocket hijacking, missing TLS |
| 2 | **DHARMA** — Permissions | Monolithic agent access, privilege escalation |
| 3 | **SANGHA** — Skill Vetting | Malicious skills, supply chain attacks |
| 4 | **KARMA** — Cost Controls | Runaway API costs, unthrottled cron jobs |
| 5 | **SILA** — Audit Trail | Invisible agent actions, memory poisoning |
| 6 | **METTA** — Identity | Agent spoofing, unverified communication |
| 7 | **BODHI** — Isolation | Lateral movement, sandbox bypass |
| 8 | **NIRVANA** — Recovery | No rollback, no kill switch, no incident response |

These aren't hypothetical. Every layer maps to a real vulnerability that was publicly exploited or disclosed in the past seven days.

We're publishing the full Sammā Suit framework as an open-source governance SDK. Not because we want to compete with OpenClaw — but because the market needs governed agents, and someone needs to show what that looks like.

---

## What We're Building

**DOORMAN** is our answer, powered by the **Sammā Suit** — eight layers of Right Protection for your AI agents. It delivers every feature OpenClaw offers — multi-channel messaging, persistent memory, proactive heartbeats, extensible skills, system access, model agnosticism, self-hosting — with all eight armor layers active from day one.

Not a wrapper. Not a patch. A platform built on the same architecture we use to run 16 agents in production.

The philosophy is simple, borrowed from how we compensate our genre agents: **agents earn for outcomes, not activity.** An agent that sends 120,000 tokens to check the time is not productive. An agent that gets a track placed on a playlist is. The Sammā Suit's cost controls, permission scoping, and audit trails all flow from this principle.

We're releasing it in phases:

1. **Open-source Sammā Suit SDK** — the eight-layer framework, free, on GitHub at **sammasuit.com**. Use it with OpenClaw, use it with anything.
2. **Doorman Pro** — managed hosting with the full Sammā Suit, vetted skill marketplace, cost dashboard, audit logs. $29/month.
3. **Doorman Enterprise** — SSO, compliance reporting, custom policies, SUTRA token integration. For the 22% of enterprises where employees are already running agents.

---

## The Invitation

OpenClaw proved that people want AI agents with real autonomy. That genie is not going back in the bottle.

The question is whether we build the infrastructure to make that autonomy safe — or whether we keep patching dumpster fires one CVE at a time.

We think the answer is obvious. And we think the team that's been running governed agents since before OpenClaw had a stable name might be the right one to build it.

The Sammā Suit framework is open source. The Discord is open. The conversation is open.

Same firepower. Built-in protection. Eight layers of Right Protection.

**— The OneZeroEight Team**

*sammasuit.com · onezeroeight.ai · discord.gg/4A6ExTnKnK · @OneZeroEight_ai*

---

### Try it now

```bash
pip install samma-suit
```

[GitHub](https://github.com/OneZeroEight-ai/samma-suit) · [sammasuit.com](https://sammasuit.com) · [Discord](https://discord.gg/4A6ExTnKnK)
