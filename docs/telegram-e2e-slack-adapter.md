# Claude Code Prompt: Telegram E2E Test + Slack Channel Adapter

## Context
The Telegram channel adapter is built and deployed (router, webhook handler, link management, conversation persistence). It needs E2E testing with a real Telegram bot. After that, we build Slack as the second messaging channel — same architecture, different API.

Both adapters route through the existing gateway. All 8 security layers enforce. One gateway, many front doors.

Backend: `C:\Users\jbwagoner\onezeroeight-backend\`
Production API: `https://api.sammasuit.com`
API Key: `samma_9300e0aa93aaa2311c6c6a51559007a7eab59e22869f13e94a1b98a5`

---

## Part 1: Telegram E2E Test

### 1A: Create a Telegram Bot

This step is manual — I need you to do it on your phone or Telegram desktop:

1. Open Telegram, search for @BotFather
2. Send `/newbot`
3. Name it: `SammaSuit Test Bot` (or whatever you want)
4. Username: `sammasuit_test_bot` (must end in `bot`, must be available)
5. BotFather gives you a token like: `7123456789:AAH...`

**Give me the bot token when you have it.**

### 1B: Link the Bot to an Agent

```bash
SAMMA_KEY="samma_9300e0aa93aaa2311c6c6a51559007a7eab59e22869f13e94a1b98a5"
API="https://api.sammasuit.com"

# Pick an agent to link — use Samma_Sentinel or create a test agent
# List agents to pick one:
curl -s -H "Authorization: Bearer $SAMMA_KEY" "$API/api/agents" | python -m json.tool | grep -E "id|name" | head -20

# Link the bot (replace BOT_TOKEN and AGENT_ID)
curl -s -X POST "$API/api/channels/telegram/link" \
  -H "Authorization: Bearer $SAMMA_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "AGENT_ID_HERE",
    "bot_token": "BOT_TOKEN_HERE"
  }' | python -m json.tool
```

Should return: `link_id`, `bot_username`, `webhook_url`. Verify the webhook was set with Telegram:

```bash
# Check webhook status directly with Telegram API
curl -s "https://api.telegram.org/botBOT_TOKEN_HERE/getWebhookInfo" | python -m json.tool
```

Should show `url` pointing to `https://api.sammasuit.com/api/channels/telegram/webhook/{link_id}`.

### 1C: Send a Test Message

Open Telegram, find your bot (@sammasuit_test_bot), and send: "Hello, what is 2 + 2?"

Check:
1. **Bot responds** — you should get a reply in Telegram
2. **Audit trail** — the interaction was logged:
```bash
curl -s -H "Authorization: Bearer $SAMMA_KEY" \
  "$API/api/agents/AGENT_ID/audit" | python -m json.tool | tail -20
```
3. **KARMA tracked cost:**
```bash
curl -s -H "Authorization: Bearer $SAMMA_KEY" \
  "$API/api/agents/AGENT_ID/budget" | python -m json.tool
```
4. **Conversation persists** — send a second message: "What did I just ask you?" The agent should remember.

### 1D: Test Enforcement via Telegram

**NIRVANA kill test:**
```bash
# Kill the agent
curl -s -X POST -H "Authorization: Bearer $SAMMA_KEY" "$API/api/agents/AGENT_ID/kill" | python -m json.tool

# Send a message in Telegram — should get an error/blocked response
# Then revive:
curl -s -X POST -H "Authorization: Bearer $SAMMA_KEY" "$API/api/agents/AGENT_ID/revive" | python -m json.tool
```

**KARMA budget test:**
```bash
# Set tiny budget
curl -s -X PUT -H "Authorization: Bearer $SAMMA_KEY" -H "Content-Type: application/json" \
  "$API/api/agents/AGENT_ID" \
  -d '{"samma_config": {"karma": {"monthly_budget_usd": 0.001}}}' | python -m json.tool

# Burn through it
curl -s -X POST -H "Authorization: Bearer $SAMMA_KEY" -H "Content-Type: application/json" \
  "$API/api/agents/AGENT_ID/usage" \
  -d '{"input_tokens": 50000, "output_tokens": 25000, "model": "claude-sonnet-4-5-20250514", "cost_usd": 1.00}' | python -m json.tool

# Send a message in Telegram — should get a budget exceeded response

# Reset budget
curl -s -X PUT -H "Authorization: Bearer $SAMMA_KEY" -H "Content-Type: application/json" \
  "$API/api/agents/AGENT_ID" \
  -d '{"samma_config": {"karma": {"monthly_budget_usd": 200.00}}}' | python -m json.tool
```

### 1E: Troubleshooting

If the bot doesn't respond:

```bash
# Check Railway logs for webhook hits
railway logs --tail 30 | grep -i "telegram\|webhook\|channel"

# Check if the webhook URL is reachable
curl -s -X POST "https://api.sammasuit.com/api/channels/telegram/webhook/LINK_ID" \
  -H "Content-Type: application/json" \
  -d '{"update_id": 1, "message": {"message_id": 1, "chat": {"id": 12345}, "text": "test", "from": {"id": 12345, "first_name": "Test"}}}' | python -m json.tool

# Check link status
curl -s -H "Authorization: Bearer $SAMMA_KEY" "$API/api/channels/telegram/links" | python -m json.tool
```

Common issues:
- `api.telegram.org` not in egress allowlist — the webhook handler needs to call sendMessage
- SSL cert issue on api.sammasuit.com — Telegram only sends webhooks to valid HTTPS
- Bot token incorrect — verify with `curl https://api.telegram.org/botTOKEN/getMe`

**Show me the results of each test before moving to Part 2.**

---

## Part 2: Slack Channel Adapter

### Architecture

Same pattern as Telegram — Slack becomes another front door into the gateway:

```
Slack user sends message in channel/DM
    ↓
Slack sends event to POST /api/channels/slack/events
    ↓
Event handler: verify signature → parse message → look up linked agent
    ↓
Forward to proxy_gateway_call() (internal, same as Telegram)
    ↓
Gateway runs all 8 security layers → LLM call → response
    ↓
Send response back via Slack Web API chat.postMessage
    ↓
Slack user sees response
```

### 2A: Slack App Setup (Manual — do this on slack.com)

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: "Sammā Suit Agent" (or whatever)
4. Pick a workspace to develop in
5. Under "OAuth & Permissions", add scopes:
   - `chat:write` — send messages
   - `app_mentions:read` — respond when @mentioned
   - `im:history` — read DM messages
   - `im:write` — send DM messages
   - `channels:history` — read channel messages (if added to a channel)
6. Under "Event Subscriptions":
   - Enable events
   - Request URL: `https://api.sammasuit.com/api/channels/slack/events` (we'll build this)
   - Subscribe to bot events: `app_mention`, `message.im`
7. Install the app to your workspace
8. Copy the **Bot User OAuth Token** (`xoxb-...`)
9. Copy the **Signing Secret** from "Basic Information"

**Give me both values when you have them.**

### 2B: Database Model

Add to `app/models/samma.py`:

```python
class SammaSlackLink(Base):
    __tablename__ = "samma_slack_links"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, ForeignKey("samma_customers.id"), nullable=False)
    agent_id = Column(String, ForeignKey("samma_agents.id"), nullable=False)
    
    # Slack credentials (encrypted)
    bot_token_encrypted = Column(Text, nullable=False)      # xoxb-... token
    signing_secret_encrypted = Column(Text, nullable=False)  # For verifying Slack requests
    
    # Slack metadata
    team_id = Column(String, nullable=True)        # Slack workspace ID
    team_name = Column(String, nullable=True)       # Slack workspace name
    bot_user_id = Column(String, nullable=True)     # Bot's Slack user ID
    
    # Conversation tracking — map Slack channel/DM to Sammā conversation
    # JSON dict: { "slack_channel_id": "samma_conversation_id", ... }
    conversation_map = Column(JSON, default=dict)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

Add migration block in `app/database.py`.

### 2C: Slack Service

Create `app/services/samma_slack.py`:

```python
"""
Slack integration service.

Handles:
- Request signature verification (HMAC-SHA256)
- Message sending via Slack Web API
- Event parsing
"""

import hashlib
import hmac
import time
import httpx

SLACK_API = "https://slack.com/api"


def verify_slack_signature(signing_secret: str, timestamp: str, body: bytes, signature: str) -> bool:
    """Verify that the request actually came from Slack."""
    # Reject requests older than 5 minutes (replay attack prevention)
    if abs(time.time() - int(timestamp)) > 300:
        return False
    
    sig_basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
    my_signature = "v0=" + hmac.new(
        signing_secret.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(my_signature, signature)


async def send_slack_message(bot_token: str, channel: str, text: str, thread_ts: str = None):
    """Send a message via Slack Web API."""
    async with httpx.AsyncClient(timeout=15) as client:
        payload = {
            "channel": channel,
            "text": text,
        }
        if thread_ts:
            payload["thread_ts"] = thread_ts  # Reply in thread
        
        resp = await client.post(
            f"{SLACK_API}/chat.postMessage",
            json=payload,
            headers={"Authorization": f"Bearer {bot_token}"}
        )
        data = resp.json()
        if not data.get("ok"):
            raise Exception(f"Slack API error: {data.get('error', 'unknown')}")
        return data


async def get_slack_bot_info(bot_token: str) -> dict:
    """Get bot user info to verify token and get bot_user_id."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"{SLACK_API}/auth.test",
            headers={"Authorization": f"Bearer {bot_token}"}
        )
        data = resp.json()
        if not data.get("ok"):
            raise Exception(f"Invalid Slack token: {data.get('error', 'unknown')}")
        return data  # {ok, url, team, team_id, user, user_id, bot_id}


def parse_slack_event(payload: dict) -> dict | None:
    """Extract message info from a Slack event payload.
    
    Returns: {channel, text, user, thread_ts, event_type} or None if not a message we should handle.
    """
    event = payload.get("event", {})
    event_type = event.get("type")
    
    # Skip bot messages (prevent loops)
    if event.get("bot_id") or event.get("subtype") == "bot_message":
        return None
    
    # Handle app_mention and direct messages
    if event_type in ("app_mention", "message"):
        text = event.get("text", "")
        
        # For app_mention, strip the @mention prefix
        if event_type == "app_mention":
            # Text looks like "<@U123ABC> what is 2+2"
            # Strip the mention
            import re
            text = re.sub(r"<@[A-Z0-9]+>\s*", "", text).strip()
        
        if not text:
            return None
        
        return {
            "channel": event.get("channel"),
            "text": text,
            "user": event.get("user"),
            "thread_ts": event.get("thread_ts") or event.get("ts"),
            "event_type": event_type
        }
    
    return None
```

### 2D: Slack Router

Create `app/routers/samma_slack.py`:

```python
# Prefix: /api/channels/slack, tags: ["samma-channels-slack"]

# POST /link — Auth'd. Validates bot token (auth.test), encrypts token + signing secret,
#   stores SammaSlackLink, returns link details + event URL
#   Body: { "agent_id": "...", "bot_token": "xoxb-...", "signing_secret": "..." }

# DELETE /link/{link_id} — Auth'd. Soft-delete (is_active=False), audit log

# GET /links — Auth'd. List all Slack links for customer

# POST /events — NO customer auth (Slack calls this). This is the event handler.
#   
#   Three responsibilities:
#   
#   1. URL Verification challenge (Slack sends this when you set the event URL):
#      If payload has "type": "url_verification", return {"challenge": payload["challenge"]}
#      This must be FAST — return immediately, no processing.
#   
#   2. Event callback:
#      - Read raw body for signature verification
#      - Verify Slack signature (HMAC-SHA256 with signing secret)
#      - Parse event to extract message
#      - Skip bot messages (prevent loops)
#      - Look up SammaSlackLink by team_id
#      - Decrypt bot token
#      - Get or create conversation_id from conversation_map
#      - Call proxy_gateway_call() 
#      - Send response back via chat.postMessage (as background task)
#      - Always return 200 quickly (Slack retries on timeout >3 seconds)
#   
#   3. Important: Slack expects a 200 response within 3 seconds.
#      Do the heavy lifting (gateway call, response) as a background task.
#      Return 200 immediately after signature verification.

# The event handler pseudocode:
async def slack_events(request: Request, db: Session):
    body = await request.body()
    payload = json.loads(body)
    
    # 1. URL Verification
    if payload.get("type") == "url_verification":
        return {"challenge": payload["challenge"]}
    
    # 2. Find the link by team_id
    team_id = payload.get("team_id")
    link = db.query(SammaSlackLink).filter_by(team_id=team_id, is_active=True).first()
    if not link:
        return {"ok": True}
    
    # 3. Verify signature
    signing_secret = decrypt_value(link.signing_secret_encrypted)
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    signature = request.headers.get("X-Slack-Signature", "")
    if not verify_slack_signature(signing_secret, timestamp, body, signature):
        return {"ok": True}  # Silent fail, don't give attackers info
    
    # 4. Parse event
    message = parse_slack_event(payload)
    if not message:
        return {"ok": True}
    
    # 5. Fire background task and return 200 immediately
    asyncio.create_task(handle_slack_message(link, message, db))
    return {"ok": True}


async def handle_slack_message(link, message, db):
    """Background task — gateway call + Slack response."""
    agent = db.query(SammaAgent).filter_by(id=link.agent_id).first()
    customer = db.query(SammaCustomer).filter_by(id=link.customer_id).first()
    
    # Get or create conversation_id for this Slack channel
    conv_map = link.conversation_map or {}
    conversation_id = conv_map.get(message["channel"])
    
    try:
        result = await proxy_gateway_call(
            agent=agent,
            customer=customer,
            messages=[{"role": "user", "content": message["text"]}],
            conversation_id=conversation_id,
            db=db
        )
        
        # Store conversation_id for persistence
        new_conv_id = result.get("conversation_id")
        if new_conv_id and new_conv_id != conversation_id:
            conv_map[message["channel"]] = new_conv_id
            link.conversation_map = conv_map
            flag_modified(link, "conversation_map")
            db.commit()
        
        # Extract response text
        response_text = extract_response_text(result)
        
    except HTTPException as e:
        response_text = f"⚠️ {e.detail.get('message', str(e.detail)) if isinstance(e.detail, dict) else str(e.detail)}"
    except Exception as e:
        response_text = f"⚠️ An error occurred: {str(e)[:200]}"
    
    # Send response to Slack (in thread)
    bot_token = decrypt_value(link.bot_token_encrypted)
    await send_slack_message(
        bot_token,
        message["channel"],
        response_text,
        thread_ts=message.get("thread_ts")
    )
```

### 2E: Register Router + Egress

In `app/main.py`:
```python
from app.routers import samma_slack
app.include_router(samma_slack.router)
```

Add `slack.com` to any egress allowlist (the event handler needs to call `https://slack.com/api/chat.postMessage`).

### 2F: Tests

```python
# tests/test_slack_channel.py

def test_slack_url_verification():
    """POST /events with url_verification returns challenge"""

def test_slack_link_creates_entry():
    """POST /link stores encrypted tokens and calls auth.test"""

def test_slack_link_invalid_token():
    """POST /link with bad token returns 400"""

def test_slack_unlink():
    """DELETE /link/{id} soft-deletes"""

def test_slack_list_links():
    """GET /links returns customer's active links"""

def test_slack_signature_verification():
    """Valid HMAC-SHA256 signature passes, invalid fails"""

def test_slack_event_routes_to_gateway():
    """Message event triggers gateway call and Slack response"""

def test_slack_skip_bot_messages():
    """Bot messages are ignored (no infinite loops)"""

def test_slack_conversation_persistence():
    """Second message in same channel reuses conversation_id"""

def test_slack_app_mention_strips_prefix():
    """@mention prefix is stripped from message text"""

def test_slack_killed_agent_responds():
    """Killed agent sends error message back to Slack"""

def test_slack_budget_exceeded_responds():
    """Budget exceeded sends error message back to Slack"""

def test_slack_returns_200_quickly():
    """Event endpoint returns 200 before gateway call completes"""
```

### 2G: Dashboard UI — Slack Integration

Add a "Slack" section alongside Telegram in the agent channels/integrations area:

```
┌─────────────────────────────────────────────────┐
│ Slack Integration                                │
│                                                  │
│ 1. Create a Slack App:                          │
│    https://api.slack.com/apps → Create New App  │
│                                                  │
│ Bot Token (xoxb-...):                           │
│ [paste token here                     ]         │
│                                                  │
│ Signing Secret:                                  │
│ [paste secret here                    ]         │
│                                                  │
│ Agent: [Samma_Sentinel ▾]                        │
│                                                  │
│                               [Connect]          │
│                                                  │
│ Status: ● Connected (workspace: My Team)        │
│ Event URL: https://api.sammasuit.com/api/...    │
│                         [Disconnect]             │
│                                                  │
│ After connecting, set this Event URL in your    │
│ Slack App settings under Event Subscriptions.   │
└─────────────────────────────────────────────────┘
```

---

## Order of Operations

1. **Part 1A-1E** — Telegram E2E test (needs manual @BotFather step)
2. **Part 2B** — Slack database model + migration
3. **Part 2C** — Slack service (signature verification, message sending, event parsing)
4. **Part 2D** — Slack router (link CRUD + event handler)
5. **Part 2E** — Register router + egress
6. **Part 2F** — Tests
7. **Deploy backend** — Push and deploy to Railway
8. **Part 2A** — Create Slack app (manual step on slack.com)
9. **Link Slack app** — via API
10. **Test in Slack** — send message, verify response + audit trail + KARMA
11. **Part 2G** — Dashboard UI for both Telegram and Slack
12. **Push frontend** — Commit and push to GitHub Pages

**Start with Part 1A — tell me you need the Telegram bot token, and I'll provide it. Then run the E2E tests. Only move to Part 2 after Telegram is verified working.**

## Important Notes

- **Slack requires 200 response within 3 seconds.** All heavy processing (gateway call, LLM, response) must be in a background task. Return 200 immediately after signature verification.
- **Slack retries on failure.** If you return non-200, Slack retries up to 3 times with increasing delays. Always return 200 even on errors.
- **Prevent bot loops.** Skip any event with `bot_id` set or `subtype: bot_message`. Otherwise the bot responds to itself infinitely.
- **Thread replies.** Use `thread_ts` to reply in-thread. This keeps conversations organized and prevents channel spam.
- **Signature verification is mandatory.** Unlike Telegram (which uses secret URL paths), Slack sends events to a public URL and authenticates via HMAC-SHA256. Never skip verification.
- **URL Verification challenge** must return immediately with the challenge value. Slack sends this once when you configure the event URL. No auth, no processing — just echo the challenge.
- **Two egress domains needed:** `slack.com` for the Web API and `api.telegram.org` for Telegram (verify it's already there from the Telegram adapter).
