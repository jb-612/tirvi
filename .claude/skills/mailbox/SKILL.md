# Mailbox — Cross-Session Messaging

Redis-backed messaging system for communication between Claude Code sessions.
Auto-provisioned per project via SessionStart hook.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Redis (localhost:6379)             │
│                                                     │
│  mailbox:{project}:incoming     ← Stream (external) │
│  mailbox:{project}:internal     ← Stream (sessions) │
│  mailbox:{project}:outgoing     ← Pub/Sub (broadcast│
│  mailbox:{project}:*:status     ← Hash (action FSM) │
│  mailbox:{project}:meta         ← JSON metadata     │
│  mailbox:projects               ← Set (global index)│
└───────┬──────────────┬──────────────┬───────────────┘
        │              │              │
   Session A      Session B      External Agent
   (same project) (same project) (other project)
```

## Folders

| Folder | Stream Key | Purpose |
|--------|-----------|---------|
| `incoming` | `mailbox:{project}:incoming` | Messages from other projects or external agents |
| `internal` | `mailbox:{project}:internal` | Same-project communication across CLI sessions |
| `outgoing` | `mailbox:{project}:outgoing` | Real-time Pub/Sub broadcast to subscribers |

## Message Schema

Every stream entry has these fields:

| Field | Required | Values | Description |
|-------|----------|--------|-------------|
| `kind` | yes | `info`, `action`, `response` | Message type |
| `from` | yes | session ID or agent name | Sender identity |
| `body` | yes | free text | Message content |
| `ts` | yes | ISO 8601 UTC | Timestamp |
| `ref_id` | response only | stream entry ID | References the original action message |

## Action Lifecycle

```
  ┌──────────┐      ┌──────────┐      ┌──────────┐
  │  SENDER  │      │  REDIS   │      │ RECEIVER │
  └────┬─────┘      └────┬─────┘      └────┬─────┘
       │                  │                  │
       │  XADD kind=action│                  │
       │─────────────────>│                  │
       │  HSET status     │                  │
       │  = "pending"     │                  │
       │─────────────────>│                  │
       │                  │  read --pending  │
       │                  │<─────────────────│
       │                  │  returns msg     │
       │                  │─────────────────>│
       │                  │                  │
       │                  │  mailbox-complete │
       │                  │  HSET = "complete"│
       │                  │<─────────────────│
       │                  │  XADD kind=      │
       │                  │  response+ref_id │
       │                  │<─────────────────│
       │                  │                  │
       │  read shows:     │                  │
       │  original=complete                  │
       │  + response msg  │                  │
       │<─────────────────│                  │
```

## CLI Scripts

All scripts are in `~/.claude/scripts/` (user-level, all projects).

### mailbox-init.sh (SessionStart hook)

Auto-provisions mailbox on session start. Reports pending actions if exists.

```bash
# Output on first run:
=== Mailbox [axon-neo]: created (incoming + internal + pub/sub) ===

# Output on subsequent runs:
=== Mailbox [axon-neo]: incoming=4 internal=3 | actions pending: incoming:1 ===
```

### mailbox-send.sh

```bash
# Send info (default)
mailbox-send.sh "Phase 2 is merged and green"

# Send action requiring response
mailbox-send.sh --kind action "Review the FK cascade strategy in F01-db-port"

# Send to incoming folder (cross-project)
mailbox-send.sh --folder incoming --kind action --from "agent-x" "Shared lib updated"

# Send to specific project
mailbox-send.sh --to other-project --kind info "Build artifact ready"
```

**Options:**
| Flag | Default | Values |
|------|---------|--------|
| `--folder` | `internal` | `incoming`, `internal` |
| `--kind` | `info` | `info`, `action` |
| `--to` | current project | any project name |
| `--from` | session ID | any identifier |

### mailbox-read.sh

```bash
# Read all internal messages (default)
mailbox-read.sh

# Read only pending actions
mailbox-read.sh --pending

# Read incoming folder
mailbox-read.sh --folder incoming

# Filter by kind
mailbox-read.sh --kind action

# Read from specific project
mailbox-read.sh --project other-project --folder incoming

# Limit results
mailbox-read.sh --count 5
```

**Options:**
| Flag | Default | Values |
|------|---------|--------|
| `--folder` | `internal` | `incoming`, `internal` |
| `--kind` | `all` | `info`, `action`, `all` |
| `--pending` | false | show only pending actions |
| `--count` | `20` | max messages to return |
| `--project` | current project | any project name |

### mailbox-complete.sh

```bash
# Mark action complete with summary
mailbox-complete.sh <message-id> "Reviewed and approved. FK cascades look correct."

# Complete on incoming folder
mailbox-complete.sh --folder incoming <message-id> "Deployed, health check green"
```

**Options:**
| Flag | Default | Values |
|------|---------|--------|
| `--folder` | `internal` | `incoming`, `internal` |
| `--project` | current project | any project name |
| `--from` | session ID | any identifier |

### mailbox-list.sh

```bash
# Table format
mailbox-list.sh
# PROJECT                        PENDING
# axon-neo                       2
# other-project                  0

# JSON format
mailbox-list.sh --json
```

## Redis MCP Integration

From any Claude Code session, use the Redis MCP tools directly:

```
# Read messages
mcp__redis__xrange  key=mailbox:axon-neo:internal  count=10

# Send a message
mcp__redis__xadd  key=mailbox:axon-neo:internal  fields={kind:action, from:session-1, body:"review this"}

# Check pending actions
mcp__redis__hgetall  name=mailbox:axon-neo:internal:status

# List all projects
mcp__redis__smembers  name=mailbox:projects

# Complete an action
mcp__redis__hset  name=mailbox:axon-neo:internal:status  key=<msg-id>  value=complete
```

## Configuration

### User-level settings (~/.claude/settings.json)

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/scripts/mailbox-init.sh"
          }
        ]
      }
    ]
  }
}
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_CLI` | `redis-cli` | Path to redis-cli binary |
| `REDIS_HOST` | `localhost` | Redis server host |
| `REDIS_PORT` | `6379` | Redis server port |
| `CLAUDE_SESSION_ID` | `session-$$` | Session identifier for `from` field |
| `MAILBOX_FROM` | session ID | Override sender identity |

## Design Decisions

See [ADR-010](../../../docs/ADR/ADR-010-redis-mailbox-cross-session-messaging.md)
for full rationale.

- **Redis Streams** over Lists: ordered, persistent, supports consumer groups
- **Pub/Sub** for outgoing: real-time broadcast, fire-and-forget
- **Status hash** for actions: Streams are append-only, hash tracks mutable state
- **User-level** not project-level: universal across all projects
- **Graceful degradation**: hook exits 0 if Redis unavailable
- **Lowercase project names**: avoids case-sensitivity issues across OS
