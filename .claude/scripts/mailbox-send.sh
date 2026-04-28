#!/usr/bin/env bash
# mailbox-send.sh — Send a message to a project mailbox
#
# Usage:
#   mailbox-send.sh [--folder incoming|internal] [--kind info|action] [--to project] "message body"
#   mailbox-send.sh --folder internal --kind action "Please review the dispatch adapter changes"
#
# Defaults: folder=internal, kind=info, project=current directory

set -euo pipefail

REDIS_CLI="${REDIS_CLI:-redis-cli}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

redis_cmd() {
  "$REDIS_CLI" -h "$REDIS_HOST" -p "$REDIS_PORT" "$@" 2>/dev/null
}

# Defaults
FOLDER="internal"
KIND="info"
PROJECT="$(basename "$PWD" | tr '[:upper:]' '[:lower:]')"
SESSION_ID="${CLAUDE_SESSION_ID:-session-$$}"
FROM="${MAILBOX_FROM:-${SESSION_ID}}"

# Parse args
while [[ $# -gt 1 ]]; do
  case "$1" in
    --folder) FOLDER="$2"; shift 2 ;;
    --kind)   KIND="$2";   shift 2 ;;
    --to)     PROJECT="$2"; shift 2 ;;
    --from)   FROM="$2";   shift 2 ;;
    *) break ;;
  esac
done

BODY="${1:?Usage: mailbox-send.sh [options] \"message body\"}"
STREAM="mailbox:${PROJECT}:${FOLDER}"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Validate
if [[ "$KIND" != "info" && "$KIND" != "action" ]]; then
  echo "Error: --kind must be 'info' or 'action'" >&2
  exit 1
fi
if [[ "$FOLDER" != "incoming" && "$FOLDER" != "internal" ]]; then
  echo "Error: --folder must be 'incoming' or 'internal'" >&2
  exit 1
fi

# Send message
MSG_ID=$(redis_cmd XADD "$STREAM" '*' \
  kind "$KIND" \
  from "$FROM" \
  body "$BODY" \
  ts "$TS")

if [ -z "$MSG_ID" ]; then
  echo "Error: failed to send message" >&2
  exit 1
fi

# If action, track status as pending
if [ "$KIND" = "action" ]; then
  redis_cmd HSET "mailbox:${PROJECT}:${FOLDER}:status" "$MSG_ID" "pending" > /dev/null
fi

echo "${MSG_ID} [${KIND}] → ${STREAM}"
