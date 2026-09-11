#!/usr/bin/env bash
# Create a worktree for one bounded unit beside the primary checkout.
# Usage: scripts/worktree.sh <branch> [base-ref]
# The worktree shares the primary .venv and hardlinks the git-ignored source
# populations, which exist only in the primary checkout. Hardlinks, not
# symlinks: a resolved source path must stay inside the worktree's own root.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
branch="${1:?usage: scripts/worktree.sh <branch> [base-ref]}"
base="${2:-origin/main}"
dir="$(dirname "$root")/CORDON-worktrees/${branch//\//-}"
git -C "$root" fetch -q origin
git -C "$root" worktree add --no-track -b "$branch" "$dir" "$base"
ln -s "$root/.venv" "$dir/.venv"
git -C "$root" ls-files -o -i --exclude-standard -z -- corpus/sources | while IFS= read -r -d '' rel; do
  mkdir -p "$dir/$(dirname "$rel")"
  ln "$root/$rel" "$dir/$rel"
done
python3 "$dir/scripts/generate_stage_b.py" >/dev/null
# A plan-first unit has no diff yet; GitHub needs one commit before a pull request can exist.
git -C "$dir" commit -q --allow-empty -m "Open unit: $branch (plan in the pull request)"
echo "$dir"
