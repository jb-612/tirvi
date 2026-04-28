#!/usr/bin/env bash
# mailbox-init.sh — Claude Code startup hook
# Auto-provisions a Redis mailbox for the current project.
#
# Key structure:
#   mailbox:{project}:incoming          — Stream (cross-project messages)
#   mailbox:{project}:internal          — Stream (same-project, cross-session)
#   mailbox:{project}:internal:status   — Hash  (msg_id → pending|complete)
#   mailbox:{project}:outgoing          — Pub/Sub channel (broadcast)
#   mailbox:{project}:meta              — JSON metadata
#   mailbox:projects                    — Set of all provisioned project names
#
# Requires: redis-cli on PATH, Redis running on localhost:6379

set -euo pipefail

REDIS_CLI="${REDIS_CLI:-redis-cli}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

redis_cmd() {
  "$REDIS_CLI" -h "$REDIS_HOST" -p "$REDIS_PORT" "$@" 2>/dev/null
}

# Derive project name from working directory basename (lowercase for consistency)
PROJECT="$(basename "$PWD" | tr '[:upper:]' '[:lower:]')"

# Session ID: PID-based for this CLI session
SESSION_ID="${CLAUDE_SESSION_ID:-session-$$}"

# Check Redis is reachable
if ! redis_cmd ping | grep -q PONG; then
  echo "=== Mailbox: Redis unavailable, skipping ==="
  exit 0
fi

# Check if mailbox already exists
EXISTS=$(redis_cmd EXISTS "mailbox:${PROJECT}:meta")

if [ "$EXISTS" = "1" ]; then
  # Mailbox exists — report pending counts per folder
  INC_LEN=$(redis_cmd XLEN "mailbox:${PROJECT}:incoming" 2>/dev/null || echo "0")
  INT_LEN=$(redis_cmd XLEN "mailbox:${PROJECT}:internal" 2>/dev/null || echo "0")

  # Count pending actions across both folders
  INC_PENDING=0
  INT_PENDING=0
  INC_STATUSES=$(redis_cmd HVALS "mailbox:${PROJECT}:incoming:status" 2>/dev/null || echo "")
  INT_STATUSES=$(redis_cmd HVALS "mailbox:${PROJECT}:internal:status" 2>/dev/null || echo "")
  [ -n "$INC_STATUSES" ] && INC_PENDING=$(echo "$INC_STATUSES" | grep -c "^pending$" || true)
  [ -n "$INT_STATUSES" ] && INT_PENDING=$(echo "$INT_STATUSES" | grep -c "^pending$" || true)
  TOTAL_PENDING=$((INC_PENDING + INT_PENDING))

  DETAIL=""
  [ "$INC_PENDING" -gt 0 ] && DETAIL="${DETAIL} incoming:${INC_PENDING}"
  [ "$INT_PENDING" -gt 0 ] && DETAIL="${DETAIL} internal:${INT_PENDING}"
  [ -z "$DETAIL" ] && DETAIL=" none"

  echo "=== Mailbox [${PROJECT}]: incoming=${INC_LEN} internal=${INT_LEN} | actions pending:${DETAIL} ==="
  exit 0
fi

# Create mailbox — seed incoming stream
redis_cmd XADD "mailbox:${PROJECT}:incoming" '*' \
  type init \
  kind info \
  from system \
  body "mailbox created for project ${PROJECT}" \
  ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  > /dev/null

# Seed internal stream
redis_cmd XADD "mailbox:${PROJECT}:internal" '*' \
  type init \
  kind info \
  from system \
  body "internal channel created for cross-session communication" \
  ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  > /dev/null

# Set metadata
redis_cmd SET "mailbox:${PROJECT}:meta" \
  "{\"project\":\"${PROJECT}\",\"created\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"folders\":{\"incoming\":\"mailbox:${PROJECT}:incoming\",\"internal\":\"mailbox:${PROJECT}:internal\",\"outgoing\":\"mailbox:${PROJECT}:outgoing\"},\"status_hash\":\"mailbox:${PROJECT}:internal:status\"}" \
  > /dev/null

# Register in global project set
redis_cmd SADD "mailbox:projects" "$PROJECT" > /dev/null

echo "=== Mailbox [${PROJECT}]: created (incoming + internal + pub/sub) ==="
