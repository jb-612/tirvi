#!/usr/bin/env bash
# mailbox-list.sh — List all project mailboxes from Redis
#
# Usage: mailbox-list.sh [--json]
#
# Reads the mailbox:projects set and prints each project's
# mailbox status (pending message count).

set -euo pipefail

REDIS_CLI="${REDIS_CLI:-redis-cli}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

redis_cmd() {
  "$REDIS_CLI" -h "$REDIS_HOST" -p "$REDIS_PORT" "$@" 2>/dev/null
}

if ! redis_cmd ping | grep -q PONG; then
  echo "Error: Redis unavailable at ${REDIS_HOST}:${REDIS_PORT}" >&2
  exit 1
fi

PROJECTS=$(redis_cmd SMEMBERS "mailbox:projects")

if [ -z "$PROJECTS" ]; then
  echo "No project mailboxes found."
  exit 0
fi

if [ "${1:-}" = "--json" ]; then
  echo "["
  FIRST=true
  while IFS= read -r proj; do
    [ -z "$proj" ] && continue
    LEN=$(redis_cmd XLEN "mailbox:${proj}:incoming" 2>/dev/null || echo "0")
    META=$(redis_cmd GET "mailbox:${proj}:meta" 2>/dev/null || echo "")
    [ -z "$META" ] && META="{}"
    if [ "$FIRST" = true ]; then
      FIRST=false
    else
      echo ","
    fi
    echo "  {\"project\":\"${proj}\",\"pending\":${LEN},\"meta\":${META}}"
  done <<< "$PROJECTS"
  echo ""
  echo "]"
else
  printf "%-30s %s\n" "PROJECT" "PENDING"
  printf "%-30s %s\n" "-------" "-------"
  while IFS= read -r proj; do
    [ -z "$proj" ] && continue
    LEN=$(redis_cmd XLEN "mailbox:${proj}:incoming" 2>/dev/null || echo "0")
    printf "%-30s %s\n" "$proj" "$LEN"
  done <<< "$PROJECTS"
fi
