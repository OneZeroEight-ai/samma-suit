# Claude Code Prompt: Chat UX Overhaul + Security Status Bar + Heartbeat System

## Context
Three features in one prompt. The dashboard chat needs UX fixes (conversation navigation, markdown rendering), the security layer badges need to be replaced with a compact status bar, and we need a governed heartbeat system so agents can take autonomous actions on a schedule.

Frontend: `C:\Users\jbwagoner\samma-suit-deploy\docs\dashboard.html`
Backend: `C:\Users\jbwagoner\onezeroeight-backend\`
Production API: `https://api.sammasuit.com`

---

## Part 1: Chat Panel UX Fixes

### 1A: Conversation List → Expandable Chat History

Currently conversations show as a flat list of titles at the top of the chat panel, mixed in with messages. Change to a proper chat navigation:

**Mobile flow (primary — test at iPhone 12/13 viewport):**
- First view: conversation list (title + timestamp + message count for each)
- Tapping a conversation opens it full-screen with messages
- Back arrow at top returns to the conversation list
- "+ New Conversation" stays at the top of the list view

**Desktop flow:**
- Same as mobile but the chat panel is already in a sidebar, so the conversation list and message view can share the same panel space

**Message display in an open conversation:**
- Messages fill the area between the header and input box
- Scrollable — newest messages at the bottom
- Scroll up for history
- User messages aligned right, assistant messages aligned left
- Each message shows timestamp

Find the current conversation rendering:
```bash
grep -n "conversation\|conv.*list\|chat.*history\|loadConv\|formatConv\|message.*append" C:\Users\jbwagoner\samma-suit-deploy\docs\dashboard.html | head -30
```

### 1B: Markdown Rendering

Agent responses show raw markdown instead of rendered HTML.

**Add marked.js via CDN:**
```html
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/dompurify/dist/purify.min.js"></script>
```

**Apply to all assistant messages:**
- Find where assistant message content is inserted into the DOM
- Instead of `element.textContent = message`, use:
```javascript
element.innerHTML = DOMPurify.sanitize(marked.parse(message));
```

**Add CSS for rendered markdown inside chat bubbles:**
```css
.chat-message-assistant pre {
    background: #1a1a2e;
    border-radius: 6px;
    padding: 10px;
    overflow-x: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
}
.chat-message-assistant code {
    background: #1a1a2e;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
}
.chat-message-assistant ul, .chat-message-assistant ol {
    padding-left: 20px;
    margin: 8px 0;
}
.chat-message-assistant a {
    color: #a855f7;
    text-decoration: underline;
}
.chat-message-assistant strong { font-weight: 700; }
.chat-message-assistant em { font-style: italic; }
```

---

## Part 2: Security Status Bar (Replace Layer Badges)

**CURRENT:** 8 colored badges taking up 2 rows at the bottom of each assistant message:
```
SUTRA ✓  NIRVANA ✓  SANGHA ✓  KARMA ✓
DHARMA ✓  BODHI ✓  METTA ✓  SILA ✓
```

**NEW:** A single horizontal bar made of 8 segments lined up end to end. Total width = message bubble width. Each segment represents one layer in fixed order: SUTRA, NIRVANA, SANGHA, KARMA, DHARMA, BODHI, METTA, SILA.

**Visual behavior:**
- All layers passed: 8 flat segments in a thin horizontal line (2-3px tall), each segment its own color. Looks like a thin rainbow status bar.
- Layer had a warning: that segment rises to ~8px tall (small bump)
- Layer had an error/block: that segment rises to ~16px tall (noticeable spike)
- Layer was skipped/not applicable: that segment is gray/dimmed, stays at 2px

**CSS implementation:**
```css
.security-bar {
    display: flex;
    width: 100%;
    height: 16px;
    align-items: flex-end;
    gap: 1px;
    margin-top: 8px;
    cursor: pointer;
}
.security-bar .segment {
    flex: 1;
    min-height: 2px;
    border-radius: 1px 1px 0 0;
    transition: height 0.2s ease;
    position: relative;
}
.security-bar .segment.pass { height: 2px; }
.security-bar .segment.warn { height: 8px; }
.security-bar .segment.error { height: 16px; }
.security-bar .segment.skip { height: 2px; opacity: 0.3; }

/* Tooltip on hover/tap */
.security-bar .segment:hover::after,
.security-bar .segment:active::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    background: #111;
    color: #fff;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 11px;
    white-space: nowrap;
    z-index: 100;
    pointer-events: none;
}
```

**Layer colors** (use the same colors currently used for the badges):
```javascript
const LAYER_COLORS = {
    sutra: '#06b6d4',    // cyan
    nirvana: '#ef4444',  // red
    sangha: '#22c55e',   // green
    karma: '#eab308',    // yellow
    dharma: '#3b82f6',   // blue
    bodhi: '#8b5cf6',    // purple
    metta: '#f97316',    // orange
    sila: '#ec4899'      // pink
};
```

**Tooltip content** — include the layer name and relevant detail if available:
```javascript
// Examples:
// "SUTRA ✓ — Gateway passed"
// "KARMA ✓ — $0.27 of $10.00"
// "NIRVANA ✗ — Agent terminated"
// "SANGHA ✓ — 2 skills approved"
```

**Find where badges are currently generated** and replace:
```bash
grep -n "SUTRA\|NIRVANA\|SANGHA\|badge\|layer.*check\|enforcement" C:\Users\jbwagoner\samma-suit-deploy\docs\dashboard.html | head -20
```

The data is already in the gateway response — the layer enforcement results. Parse those same results into the new bar format instead of badges.

---

## Part 3: Governed Heartbeat System

### 3A: Database Model

Add to `app/models/samma.py`:

```python
class SammaHeartbeat(Base):
    __tablename__ = "samma_heartbeats"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, ForeignKey("samma_agents.id"), nullable=False)
    customer_id = Column(String, ForeignKey("samma_customers.id"), nullable=False)
    
    # Schedule
    enabled = Column(Boolean, default=False)
    interval_minutes = Column(Integer, default=240)  # Default: 4 hours
    
    # Heartbeat prompt — what the agent does when it wakes up
    prompt = Column(Text, nullable=False)
    
    # State
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    last_result = Column(Text, nullable=True)  # Summary of what happened
    last_cost_usd = Column(Float, default=0.0)
    consecutive_failures = Column(Integer, default=0)
    
    # Limits
    max_cost_per_run_usd = Column(Float, default=0.50)  # Safety cap per heartbeat
    max_consecutive_failures = Column(Integer, default=3)  # Auto-disable after 3 failures
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

Add migration block in `app/database.py`.

### 3B: Heartbeat Scheduler

Create `app/services/samma_heartbeat.py`:

```python
"""
Governed Heartbeat System

Every heartbeat goes through the full gateway pipeline:
1. Check NIRVANA — is agent alive? If not, skip.
2. Check KARMA — does agent have budget? If not, skip.
3. Check per-run cost cap — will this run exceed the safety limit?
4. Call proxy_gateway_call() with the heartbeat prompt
5. The agent decides what to do (read feeds, post, comment, check tasks, etc.)
6. All 8 layers enforce on every action the agent takes
7. SILA logs the heartbeat event with cost and result
8. Update next_run_at
"""

import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

async def run_heartbeat(heartbeat_id: str, db: Session):
    """Execute a single heartbeat for an agent."""
    
    heartbeat = db.query(SammaHeartbeat).filter_by(id=heartbeat_id, enabled=True).first()
    if not heartbeat:
        return
    
    agent = db.query(SammaAgent).filter_by(id=heartbeat.agent_id).first()
    customer = db.query(SammaCustomer).filter_by(id=heartbeat.customer_id).first()
    
    if not agent or not customer:
        return
    
    # NIRVANA check — is agent alive?
    if agent.status != "active":
        heartbeat.last_result = "Skipped: agent is not active"
        heartbeat.next_run_at = datetime.now(timezone.utc) + timedelta(minutes=heartbeat.interval_minutes)
        db.commit()
        return
    
    # KARMA check — does agent have budget?
    # (The gateway will also check this, but pre-checking avoids unnecessary LLM calls)
    budget_remaining = check_budget(agent, customer, db)
    if budget_remaining <= 0:
        heartbeat.last_result = "Skipped: budget exhausted"
        heartbeat.next_run_at = datetime.now(timezone.utc) + timedelta(minutes=heartbeat.interval_minutes)
        db.commit()
        return
    
    # Execute through the gateway — all 8 layers enforce
    try:
        result = await proxy_gateway_call(
            agent=agent,
            customer=customer,
            messages=[{"role": "user", "content": heartbeat.prompt}],
            conversation_id=f"heartbeat-{heartbeat.id}",
            db=db
        )
        
        # Record success
        heartbeat.last_run_at = datetime.now(timezone.utc)
        heartbeat.next_run_at = datetime.now(timezone.utc) + timedelta(minutes=heartbeat.interval_minutes)
        heartbeat.last_result = "Success"
        heartbeat.last_cost_usd = result.get("cost_usd", 0.0)
        heartbeat.consecutive_failures = 0
        
        # Audit log
        log_audit(agent, "heartbeat_run", {
            "heartbeat_id": heartbeat.id,
            "cost_usd": heartbeat.last_cost_usd,
            "result": "success"
        }, db)
        
    except Exception as e:
        heartbeat.consecutive_failures += 1
        heartbeat.last_result = f"Error: {str(e)[:200]}"
        heartbeat.last_run_at = datetime.now(timezone.utc)
        heartbeat.next_run_at = datetime.now(timezone.utc) + timedelta(minutes=heartbeat.interval_minutes)
        
        # Auto-disable after too many failures
        if heartbeat.consecutive_failures >= heartbeat.max_consecutive_failures:
            heartbeat.enabled = False
            heartbeat.last_result = f"Auto-disabled after {heartbeat.max_consecutive_failures} consecutive failures: {str(e)[:100]}"
            log_audit(agent, "heartbeat_disabled", {
                "heartbeat_id": heartbeat.id,
                "reason": "consecutive_failures",
                "failures": heartbeat.consecutive_failures
            }, db)
        
        log_audit(agent, "heartbeat_error", {
            "heartbeat_id": heartbeat.id,
            "error": str(e)[:200]
        }, db)
    
    db.commit()


async def heartbeat_loop():
    """
    Main heartbeat scheduler loop. Runs as a background task.
    Checks every 60 seconds for heartbeats that are due.
    """
    while True:
        try:
            db = SessionLocal()
            now = datetime.now(timezone.utc)
            
            # Find all enabled heartbeats that are due
            due_heartbeats = db.query(SammaHeartbeat).filter(
                SammaHeartbeat.enabled == True,
                (SammaHeartbeat.next_run_at <= now) | (SammaHeartbeat.next_run_at == None)
            ).all()
            
            for heartbeat in due_heartbeats:
                # Run each heartbeat (could parallelize later)
                await run_heartbeat(heartbeat.id, db)
            
            db.close()
        except Exception as e:
            print(f"Heartbeat loop error: {e}")
        
        # Check again in 60 seconds
        await asyncio.sleep(60)
```

### 3C: Start Heartbeat Loop on App Startup

In `app/main.py`, add a startup event:

```python
@app.on_event("startup")
async def start_heartbeat_scheduler():
    """Start the governed heartbeat loop as a background task."""
    asyncio.create_task(heartbeat_loop())
```

### 3D: Heartbeat API Endpoints

Create `app/routers/samma_heartbeat.py`:

```python
# POST /api/agents/{id}/heartbeat — Create or update heartbeat config
# Body: {
#   "enabled": true,
#   "interval_minutes": 240,
#   "prompt": "Read the Moltbook feed and identify posts where you can add security value. For the top 3 posts, compose and post a helpful comment.",
#   "max_cost_per_run_usd": 0.50
# }
# Auth: customer auth + agent ownership check

# GET /api/agents/{id}/heartbeat — Get heartbeat config and status
# Returns: config + last_run_at + next_run_at + last_result + last_cost_usd + consecutive_failures

# POST /api/agents/{id}/heartbeat/trigger — Manually trigger a heartbeat now (for testing)
# Runs the heartbeat immediately regardless of schedule

# DELETE /api/agents/{id}/heartbeat — Disable and remove heartbeat
```

Register in `app/main.py`.

### 3E: Heartbeat Tests

```python
# tests/test_heartbeat.py

def test_create_heartbeat():
    """Create heartbeat config for an agent"""

def test_heartbeat_respects_nirvana():
    """Killed agent's heartbeat is skipped"""

def test_heartbeat_respects_karma():
    """Agent with exhausted budget is skipped"""

def test_heartbeat_auto_disables_on_failures():
    """3 consecutive failures auto-disables the heartbeat"""

def test_heartbeat_manual_trigger():
    """Manual trigger runs heartbeat immediately"""

def test_heartbeat_records_audit():
    """Heartbeat run creates SILA audit entry"""

def test_heartbeat_cost_tracking():
    """Heartbeat cost is recorded and respects per-run cap"""

def test_heartbeat_scheduling():
    """next_run_at is correctly set after each run"""
```

### 3F: Dashboard UI — Heartbeat Config

Add a "Heartbeat" section to the agent detail panel:

```
┌─────────────────────────────────────────────────┐
│ Heartbeat                                        │
│                                                  │
│ Status: ● Enabled (next run in 2h 15m)          │
│ Last run: 1:45 PM — Success ($0.12)             │
│                                                  │
│ Interval: [4 hours ▾]                            │
│ Budget per run: [$0.50 ▾]                        │
│                                                  │
│ Prompt:                                          │
│ ┌─────────────────────────────────────────────┐ │
│ │ Read the Moltbook feed and identify posts   │ │
│ │ where you can add security value...         │ │
│ └─────────────────────────────────────────────┘ │
│                                                  │
│ [Save]  [Trigger Now]  [Disable]                │
└─────────────────────────────────────────────────┘
```

---

## Order of Operations

1. **Audit current chat code** — find conversation list, message display, and badge rendering
2. **Part 1A** — Conversation list → expandable navigation with proper mobile flow
3. **Part 1B** — Add marked.js + DOMPurify, render markdown in assistant messages
4. **Part 2** — Replace layer badges with security status bar
5. **Push frontend** — Commit and push dashboard.html to GitHub Pages
6. **Part 3A** — Heartbeat database model + migration
7. **Part 3B** — Heartbeat scheduler service
8. **Part 3C** — Startup event in main.py
9. **Part 3D** — Heartbeat API endpoints
10. **Part 3E** — Tests
11. **Part 3F** — Dashboard heartbeat UI
12. **Deploy backend** — Push and deploy to Railway
13. **Test** — Create a heartbeat for Sentinel, trigger manually, verify it reads Moltbook feed and comments

**Start with Step 1 — audit the current chat code and show me what you find before making changes.**

## Important Notes

- The heartbeat loop runs inside the FastAPI process as a background task. For production scale, this should eventually move to a proper task queue (Celery, etc.), but asyncio.create_task is fine for now.
- The per-run cost cap ($0.50 default) is a safety net on TOP of KARMA's monthly budget. Even if KARMA has budget remaining, a single heartbeat run can't exceed this cap.
- Auto-disable after 3 consecutive failures prevents a broken heartbeat from burning budget on repeated errors.
- The heartbeat conversation uses `heartbeat-{id}` as conversation_id, so heartbeat history accumulates separately from user conversations.
- The heartbeat prompt is the most important config — it determines what the agent does when it wakes up. For Sentinel, it should be: "Read the Moltbook general and security feeds. Identify the top 3 posts where you can add security value with your expertise. For each, compose and post a helpful comment. Be technical and specific. Do not mention Sammā Suit unless directly asked."
