#!/usr/bin/env bash
# Create a worktree for one bounded unit beside the primary checkout.
# Usage: scripts/worktree.sh <branch> [base-ref]
# The worktree shares the primary .venv. Source bytes live in the content-addressed
# store (`$CORDON_STORE`, or `<repository>-store` beside the main checkout), which
# every worktree resolves to the same path; nothing is copied or linked.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
branch="${1:?usage: scripts/worktree.sh <branch> [base-ref]}"
base="${2:-origin/main}"
dir="$(dirname "$root")/CORDON-worktrees/${branch//\//-}"
git -C "$root" fetch -q origin
git -C "$root" worktree add --no-track -b "$branch" "$dir" "$base"
ln -s "$root/.venv" "$dir/.venv"
python3 "$dir/scripts/generate_stage_b.py" >/dev/null
# A plan-first unit has no diff yet; GitHub needs one commit before a pull request can exist.
git -C "$dir" commit -q --allow-empty -m "Open unit: $branch (plan in the pull request)"
echo "$dir"
