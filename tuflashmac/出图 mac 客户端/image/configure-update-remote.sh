#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <repo-url> [branch]"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$ROOT_DIR" rev-parse --show-toplevel)"
REMOTE_URL="$1"
BRANCH="${2:-main}"

if git -C "$REPO_ROOT" remote get-url origin >/dev/null 2>&1; then
  git -C "$REPO_ROOT" remote set-url origin "$REMOTE_URL"
else
  git -C "$REPO_ROOT" remote add origin "$REMOTE_URL"
fi

git -C "$REPO_ROOT" fetch origin
git -C "$REPO_ROOT" branch --set-upstream-to="origin/$BRANCH" "$BRANCH" >/dev/null 2>&1 || true

echo "Configured origin for $REPO_ROOT -> $REMOTE_URL (branch: $BRANCH)"
