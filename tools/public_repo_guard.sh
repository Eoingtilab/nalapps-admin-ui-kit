#!/usr/bin/env bash
set -euo pipefail

tracked="$(git ls-files)"

if printf '%s\n' "$tracked" | grep -E '(^|/)(\.env|\.env\..+|id_rsa|id_ed25519|.*\.pem|.*\.p12|.*\.pfx|.*\.sql|.*\.dump|.*\.sqlite|.*\.bak)$'; then
  echo "FAIL: secret, credential, backup, or database-like file is tracked." >&2
  exit 1
fi

if git grep -nEI '(BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,})' -- ':!docs/PUBLIC-REPOSITORY-SAFETY.md' ':!tools/public_repo_guard.sh'; then
  echo "FAIL: potential credential material found." >&2
  exit 1
fi

if git grep -nEI '(password|passwd|secret|api[_-]?key|token)[[:space:]]*[:=][[:space:]]*["'"'][^"'"']{8,}["'"']' -- '*.php' '*.json' '*.yml' '*.yaml' '*.env*' 2>/dev/null; then
  echo "FAIL: potential hard-coded secret assignment found." >&2
  exit 1
fi

printf 'PASS public_repository_safety\n'
