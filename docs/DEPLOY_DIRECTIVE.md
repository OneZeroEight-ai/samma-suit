# Claude Code Directive: Launch sammasuit.com + GitHub + Manifesto

> Run these three tasks in order. Each task should be fully complete before moving to the next.

---

## Task 1: Update & Deploy Landing Page → sammasuit.com

### 1A. Update `samma/docs/doorman_landing.html`

The landing page is production-ready but has placeholder links and a Cloudflare email-obfuscated address. Fix these:

**Replace all `href="#"` placeholder links:**
- `Contact Us` button (line ~1040) → `mailto:info@sammasuit.com`
- `Talk to Sales` button (line ~1055) → `mailto:info@sammasuit.com?subject=DOORMAN%20Enterprise%20Inquiry`

**Replace the obfuscated email in the footer (line ~1075):**
```html
<!-- REPLACE THIS: -->
<a href="/cdn-cgi/l/email-protection#..."><span class="__cf_email__" ...>[email&#160;protected]</span></a>

<!-- WITH THIS: -->
<a href="mailto:info@sammasuit.com">info@sammasuit.com</a>
```

**Update the final CTA section (line ~1065):**
Add a GitHub button alongside the Discord button:
```html
<a href="https://github.com/OneZeroEight-ai/samma-suit" class="btn btn-primary">View on GitHub</a>
<a href="https://discord.gg/4A6ExTnKnK" class="btn btn-ghost">Join the Discord</a>
```

**Update the View on GitHub button (line ~1010):**
Currently points to `https://sammasuit.com`. Change to:
```html
<a href="https://github.com/OneZeroEight-ai/samma-suit" class="btn btn-ghost">View on GitHub</a>
```

**Update the copyright line (line ~1079):**
```html
<div class="copy">© 2026 OneZeroEight.ai — DOORMAN powered by the Sammā Suit</div>
```

**Remove the Cloudflare email decode script (line ~1083):**
Delete the `<script data-cfasync="false" src="/cdn-cgi/scripts/5c5dd728/cloudflare-static/email-decode.min.js"></script>` — we're using a plain mailto now.

**Add meta tags to `<head>` for SEO and social sharing:**
```html
<meta name="description" content="DOORMAN — Eight layers of Right Protection for autonomous AI agents. The Sammā Suit security framework by OneZeroEight.">
<meta property="og:title" content="DOORMAN — Sammā Suit by OneZeroEight">
<meta property="og:description" content="Eight layers of Right Protection for autonomous AI agents. Open-source security framework.">
<meta property="og:url" content="https://sammasuit.com">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@OneZeroEight_ai">
<meta name="twitter:title" content="DOORMAN — Sammā Suit">
<meta name="twitter:description" content="Eight layers of Right Protection for autonomous AI agents.">
```

### 1B. Deploy to sammasuit.com

The domain is registered. Determine hosting setup:
- **If using Cloudflare Pages:** Create a simple static site. The entire site is one HTML file. Create an `index.html` from the updated `doorman_landing.html`. Deploy.
- **If using GitHub Pages:** Can serve from the `samma-suit` repo (see Task 2), `docs/` folder or gh-pages branch.
- **If using Railway (where the backend already lives):** Add a static file route.

Ask me which hosting approach I want before deploying. Whichever we pick, the result should be: `https://sammasuit.com` serves the updated landing page.

---

## Task 2: Create GitHub Repository — `onezeroeight/samma-suit`

### 2A. Prepare the repo

The SDK is already built in `samma/`. Structure the GitHub repo as:

```
samma-suit/
├── README.md                  # Already exists in samma/ — verify it's complete
├── LICENSE                    # Create: MIT license, copyright OneZeroEight.ai 2026
├── pyproject.toml             # Already exists
├── samma/                     # The SDK package (already built)
│   ├── __init__.py
│   ├── _version.py
│   ├── sutra/                 # Layer 1 — Gateway (implemented)
│   ├── dharma/                # Layer 2 — Permissions (implemented)
│   ├── sangha/                # Layer 3 — Skill Vetting (stub)
│   ├── karma/                 # Layer 4 — Cost Controls (stub)
│   ├── sila/                  # Layer 5 — Audit Trail (stub)
│   ├── metta/                 # Layer 6 — Identity (stub)
│   ├── bodhi/                 # Layer 7 — Isolation (stub)
│   ├── nirvana/               # Layer 8 — Recovery (stub)
│   ├── types.py
│   ├── exceptions.py
│   └── integration.py         # FastAPI SammaSuit helper
├── tests/                     # 60 passing tests
├── docs/                      # The 7 deliverables + CLAUDE.md
│   ├── CLAUDE.md
│   ├── DOORMAN_Pitch.pdf
│   ├── DOORMAN_Eight_Layer_Armor_Spec.docx
│   ├── DOORMAN_IP_Strategy.md
│   ├── doorman_landing.html   # (updated version from Task 1)
│   ├── doorman_manifesto.md
│   ├── doorman_architecture.mermaid
│   └── doorman_sutra_integration.md
├── examples/
│   └── fastapi_demo.py        # Minimal working example of mounting Sammā Suit on a FastAPI app
└── .github/
    └── FUNDING.yml             # Optional: link to SUTRA token / sponsorship
```

### 2B. Create missing files

**LICENSE (MIT):**
```
MIT License

Copyright (c) 2026 OneZeroEight.ai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**examples/fastapi_demo.py:**
Create a minimal but complete working example that demonstrates:
- Mounting the Sammā Suit on a FastAPI app
- SUTRA layer blocking a bad origin
- DHARMA layer requiring permissions on an endpoint
- A protected route and an unprotected route
- Running with `uvicorn`

Should be < 50 lines, fully commented, copy-paste-runnable.

**.github/FUNDING.yml:**
```yaml
custom: ["https://sammasuit.com", "https://sutra.exchange"]
```

**Create a .gitignore:**
Standard Python gitignore + `__pycache__`, `.env`, `*.pyc`, `dist/`, `build/`, `*.egg-info/`.

### 2C. Verify README.md

The README should include:
- The Sammā Suit name with macron (Sammā, not Samma)
- The eight layers table
- Quick install: `pip install samma-suit`
- Quick usage: mount on FastAPI in ~10 lines
- Link to sammasuit.com
- Link to docs/ for the full spec
- Badge ideas: Python 3.11+, MIT license, tests passing
- "Built by OneZeroEight.ai" with link

If the existing README is missing any of this, update it.

### 2D. Push to GitHub

```bash
cd samma-suit/
git init
git add .
git commit -m "🛡️ Sammā Suit v0.1.0 — Eight layers of Right Protection for AI agents"
git branch -M main
git remote add origin https://github.com/OneZeroEight-ai/samma-suit.git
git push -u origin main
```

Ask me to create the GitHub repo first if it doesn't exist yet.

---

## Task 3: Publish the Manifesto

### 3A. Prepare the blog post

The manifesto is at `samma/docs/doorman_manifesto.md`. It needs these updates before publishing:

**Add at the top (after the title):**
```markdown
> 🛡️ The Sammā Suit is now open source → [github.com/OneZeroEight-ai/samma-suit](https://github.com/OneZeroEight-ai/samma-suit)
> 📧 info@sammasuit.com | 🌐 sammasuit.com
```

**Add at the bottom (before the footer):**
```markdown
---

### Try it now

```bash
pip install samma-suit
```

→ [GitHub](https://github.com/OneZeroEight-ai/samma-suit) · [sammasuit.com](https://sammasuit.com) · [Discord](https://discord.gg/4A6ExTnKnK)
```

### 3B. Publish to these channels

**Hacker News:**
- Title: `Sammā Suit – Eight layers of security for AI agents (open source)`
- URL: `https://sammasuit.com` (or the GitHub repo)
- Timing: Post weekday morning US time for max visibility

**Reddit:**
- r/programming — title: "We run 16 AI agents in production. Here's what OpenClaw gets wrong, and our open-source fix."
- r/cybersecurity — title: "OpenClaw's security problems run deeper than CVE-2026-25253. We built an 8-layer alternative."
- r/Python — title: "samma-suit: Open-source security middleware for AI agents (FastAPI, 60 tests, MIT)"
- r/selfhosted — title: "Self-hosted AI agent security: 8-layer framework as an alternative to OpenClaw's approach"

**X/Twitter (@OneZeroEight_ai):**
Draft a thread (5-7 tweets):
1. Hook: OpenClaw has the right idea and the wrong architecture. We run 16 AI agents in production. Here's what we built. 🧵
2. The problem: CVE-2026-25253, 341 malicious skills, $750/mo API waste, 1.5M unsupervised agents
3. The Sammā Suit: 8 layers named for the Noble Eightfold Path. Each one stops a real attack class.
4. Layer overview (the table, compressed)
5. It's open source: `pip install samma-suit`
6. Link to manifesto + sammasuit.com + GitHub
7. "Same firepower. Built-in protection." — info@sammasuit.com

**Discord (discord.gg/4A6ExTnKnK):**
Announce in the server with link to GitHub + manifesto.

### 3C. Prepare launch text for me to review

Don't auto-post anything. Write all the copy (HN title, Reddit posts, X thread, Discord announcement) and present it for my review before I post manually.

---

## Order of Operations

1. Update the landing page HTML (Task 1A)
2. Ask me about hosting preference (Task 1B)
3. Prepare the GitHub repo files (Task 2A-C)
4. Ask me to create the GitHub repo, then push (Task 2D)
5. Update the manifesto (Task 3A)
6. Write all launch copy and present for review (Task 3C)

Do not skip the two checkpoints (hosting choice + GitHub repo creation). Everything else, execute autonomously.
