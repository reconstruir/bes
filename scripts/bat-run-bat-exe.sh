#!/bin/sh
# Portable POSIX sh -- same rationale as bat-exe-repo's own run-bat.sh: no
# bash-only syntax, so this works unmodified on Alpine (BusyBox ash, no
# bash installed by default) and any other minimal/CI target.
#
# Thin consumer wrapper: clone (or update) the bat-exe exe-repo into a
# local cache, then delegate to its own run-bat.sh. This exact script also
# lives in bes/scripts/bat-run-bat-exe.sh, unmodified, to prove the
# pattern works from a consumer repo that isn't bat itself.
set -e

# TODO: move to the public HTTPS clone URL once bat-exe's git host
# visibility is set to Public (see bat-exe-repo.md "Public, read-only for
# consumers"). SSH works today only because this machine already has a
# write-capable key configured -- a real anonymous consumer won't have it.
BAT_EXE_REPO_ADDRESS="${BAT_EXE_REPO_ADDRESS:-git@git:ramiro/bat-exe.git}"
BAT_EXE_REPO_HOME="${BAT_EXE_REPO_HOME:-$HOME/.bat/bat-exe}"

[ $# -ge 1 ] || { echo "usage: $0 <version>|latest [args...]" >&2; exit 1; }

# Quiet by default -- git prints its clone/pull progress (remote:
# Enumerating..., Updating X..Y, Fast-forward, file summaries) to stderr
# by design, so a plain -q flag isn't enough on its own for pull. Capture
# output and only show it if the command actually fails, unless DEBUG=1.
run_git() {
  if [ -n "${DEBUG:-}" ]; then
    "$@"
  else
    _out=$("$@" 2>&1) || { echo "$_out" >&2; return 1; }
  fi
}

if [ ! -d "$BAT_EXE_REPO_HOME/.git" ]; then
  mkdir -p "$(dirname "$BAT_EXE_REPO_HOME")"
  run_git env GIT_LFS_SKIP_SMUDGE=1 git clone "$BAT_EXE_REPO_ADDRESS" "$BAT_EXE_REPO_HOME"
  # Persist the skip locally so every subsequent `git pull` below stays
  # skip-smudge too, not just this initial clone -- GIT_LFS_SKIP_SMUDGE is
  # only scoped to the one invocation it's set for.
  ( cd "$BAT_EXE_REPO_HOME" && run_git git lfs install --local --skip-smudge )
else
  ( cd "$BAT_EXE_REPO_HOME" && run_git git pull )
fi

exec "$BAT_EXE_REPO_HOME/run-bat.sh" "$@"
