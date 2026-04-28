#!/usr/bin/env bash
set -euo pipefail

# PreToolUse hook for Bash — blocks dangerous shell commands
# Exit 0 = allow, Exit 2 = block

INPUT=$(cat)

CMD=$(echo "$INPUT" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(data.get('tool_input', {}).get('command', ''))
" 2>/dev/null || echo "")

if [ -z "$CMD" ]; then
  exit 0
fi

# sudo
if echo "$CMD" | grep -qE '^\s*sudo\b'; then
  echo "BLOCKED: sudo requires explicit approval" >&2
  exit 2
fi

# rm (allow only under /tmp/)
if echo "$CMD" | grep -qE '^\s*rm\b'; then
  paths=$(echo "$CMD" | grep -oE '/[^ ]+' || true)
  if [ -n "$paths" ]; then
    while IFS= read -r p; do
      if [[ "$p" != /tmp/* ]]; then
        echo "BLOCKED: rm outside /tmp/ is not allowed. Path: $p" >&2
        exit 2
      fi
    done <<< "$paths"
  else
    echo "BLOCKED: rm with relative paths is not allowed" >&2
    exit 2
  fi
fi

# rmdir
if echo "$CMD" | grep -qE '^\s*rmdir\b'; then
  echo "BLOCKED: rmdir requires explicit approval" >&2
  exit 2
fi

# chmod 777
if echo "$CMD" | grep -qE 'chmod\s+777'; then
  echo "BLOCKED: chmod 777 is not allowed" >&2
  exit 2
fi

# Force kill
if echo "$CMD" | grep -qE '(kill\s+-9|pkill|killall)\b'; then
  echo "BLOCKED: Force kill requires explicit approval" >&2
  exit 2
fi

# Dangerous git commands
if echo "$CMD" | grep -qE 'git\s+push\s+--force'; then
  echo "BLOCKED: git push --force requires explicit approval" >&2
  exit 2
fi
if echo "$CMD" | grep -qE 'git\s+reset\s+--hard'; then
  echo "BLOCKED: git reset --hard requires explicit approval" >&2
  exit 2
fi
if echo "$CMD" | grep -qE 'git\s+clean\s+-f'; then
  echo "BLOCKED: git clean -f requires explicit approval" >&2
  exit 2
fi

# Disk operations
if echo "$CMD" | grep -qE '^\s*(dd|mkfs)\b'; then
  echo "BLOCKED: disk operations require explicit approval" >&2
  exit 2
fi

# System shutdown/reboot
if echo "$CMD" | grep -qE '^\s*(shutdown|reboot)\b'; then
  echo "BLOCKED: system shutdown/reboot not allowed" >&2
  exit 2
fi

# macOS service management
if echo "$CMD" | grep -qE '^\s*launchctl\b'; then
  echo "BLOCKED: launchctl service management not allowed" >&2
  exit 2
fi

# Python-specific dangerous commands
if echo "$CMD" | grep -qE 'pip\s+uninstall\b'; then
  echo "BLOCKED: pip uninstall requires explicit approval" >&2
  exit 2
fi
if echo "$CMD" | grep -qE 'pip\s+install\s+--force-reinstall'; then
  echo "BLOCKED: pip install --force-reinstall requires explicit approval" >&2
  exit 2
fi

exit 0
