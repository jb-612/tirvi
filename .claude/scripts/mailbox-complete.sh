#!/usr/bin/env bash
# mailbox-complete.sh — Mark an action message as complete and post response
#
# Usage:
#   mailbox-complete.sh <message-id> "summary of what was done"
#   mailbox-complete.sh --folder incoming <message-id> "summary"
#
# Marks the original action message as complete in the status hash,
# then posts a response message referencing the original.

set -euo pipefail

REDIS_CLI="${REDIS_CLI:-redis-cli}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

redis_cmd() {
  "$REDIS_CLI" -h "$REDIS_HOST" -p "$REDIS_PORT" "$@" 2>/dev/null
}

# Defaults
FOLDER="internal"
PROJECT="$(basename "$PWD" | tr '[:upper:]' '[:lower:]')"
SESSION_ID="${CLAUDE_SESSION_ID:-session-$$}"
FROM="${MAILBOX_FROM:-${SESSION_ID}}"

# Parse args
while [[ $# -gt 2 ]]; do
  case "$1" in
    --folder)  FOLDER="$2";  shift 2 ;;
    --project) PROJECT="$2"; shift 2 ;;
    --from)    FROM="$2";    shift 2 ;;
    *) break ;;
  esac
done

MSG_ID="${1:?Usage: mailbox-complete.sh [options] <message-id> \"summary\"}"
SUMMARY="${2:?Usage: mailbox-complete.sh [options] <message-id> \"summary\"}"

STREAM="mailbox:${PROJECT}:${FOLDER}"
STATUS_HASH="mailbox:${PROJECT}:${FOLDER}:status"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Verify the message exists and is pending
CURRENT_STATUS=$(redis_cmd HGET "$STATUS_HASH" "$MSG_ID")

if [ -z "$CURRENT_STATUS" ]; then
  echo "Error: message ${MSG_ID} not found in status hash (not an action message?)" >&2
  exit 1
fi

if [ "$CURRENT_STATUS" = "complete" ]; then
  echo "Warning: message ${MSG_ID} is already complete" >&2
  exit 0
fi

# Mark as complete
redis_cmd HSET "$STATUS_HASH" "$MSG_ID" "complete" > /dev/null

# Post response message referencing the original
RESP_ID=$(redis_cmd XADD "$STREAM" '*' \
  kind response \
  from "$FROM" \
  ref_id "$MSG_ID" \
  body "$SUMMARY" \
  ts "$TS")

echo "Completed ${MSG_ID} → response ${RESP_ID}"
