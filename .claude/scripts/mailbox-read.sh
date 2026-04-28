#!/usr/bin/env bash
# mailbox-read.sh — Read messages from a project mailbox
#
# Usage:
#   mailbox-read.sh [--folder incoming|internal] [--kind info|action|all] [--pending] [--count N] [--project name]
#
# --pending   Show only action messages with status=pending
# --count N   Number of messages to read (default: 20)
#
# Defaults: folder=internal, kind=all, project=current directory

set -euo pipefail

REDIS_CLI="${REDIS_CLI:-redis-cli}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

redis_cmd() {
  "$REDIS_CLI" -h "$REDIS_HOST" -p "$REDIS_PORT" "$@" 2>/dev/null
}

# Defaults
FOLDER="internal"
KIND_FILTER="all"
PENDING_ONLY=false
COUNT=20
PROJECT="$(basename "$PWD" | tr '[:upper:]' '[:lower:]')"

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --folder)  FOLDER="$2";      shift 2 ;;
    --kind)    KIND_FILTER="$2";  shift 2 ;;
    --pending) PENDING_ONLY=true; shift ;;
    --count)   COUNT="$2";       shift 2 ;;
    --project) PROJECT="$2";     shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

STREAM="mailbox:${PROJECT}:${FOLDER}"
STATUS_HASH="mailbox:${PROJECT}:${FOLDER}:status"

# Read stream entries (newest last)
RAW=$(redis_cmd XREVRANGE "$STREAM" '+' '-' COUNT "$COUNT")

if [ -z "$RAW" ]; then
  echo "No messages in ${STREAM}."
  exit 0
fi

# Parse and display
echo ""
printf "%-20s %-8s %-15s %-10s %s\n" "ID" "KIND" "FROM" "STATUS" "BODY"
printf "%-20s %-8s %-15s %-10s %s\n" "---" "----" "----" "------" "----"

# Parse redis XREVRANGE output (pairs of id + field array)
echo "$RAW" | redis_cmd --no-auth-warning -h "$REDIS_HOST" -p "$REDIS_PORT" \
  XREVRANGE "$STREAM" '+' '-' COUNT "$COUNT" 2>/dev/null | \
  awk '
  /^[0-9]+-[0-9]+$/ { id=$0; next }
  ' 2>/dev/null || true

# Simpler approach: use a Lua-like pipeline with xrange
# Since bash parsing of XRANGE is clunky, use a small redis script
redis_cmd EVAL '
local stream = KEYS[1]
local status_hash = KEYS[2]
local count = tonumber(ARGV[1])
local kind_filter = ARGV[2]
local pending_only = ARGV[3] == "true"

local entries = redis.call("XREVRANGE", stream, "+", "-", "COUNT", count)
local results = {}

for _, entry in ipairs(entries) do
  local id = entry[1]
  local fields = entry[2]
  local msg = {}
  msg["id"] = id

  for i = 1, #fields, 2 do
    msg[fields[i]] = fields[i+1]
  end

  -- Get status from hash if it exists
  local status = redis.call("HGET", status_hash, id) or "n/a"
  if not status then status = "n/a" end
  msg["status"] = status

  -- Apply filters
  local show = true
  if kind_filter ~= "all" and msg["kind"] ~= kind_filter then
    show = false
  end
  if pending_only and status ~= "pending" then
    show = false
  end

  if show then
    table.insert(results, string.format(
      "%-20s %-8s %-15s %-10s %s",
      msg["id"] or "",
      msg["kind"] or "info",
      msg["from"] or "unknown",
      msg["status"] or "n/a",
      msg["body"] or ""
    ))
  end
end

return results
' 2 "$STREAM" "$STATUS_HASH" "$COUNT" "$KIND_FILTER" "$PENDING_ONLY"
echo ""
