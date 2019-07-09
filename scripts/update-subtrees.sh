#!/bin/bash

BES_SHELL_REMOTE=bes_shell
BES_SHELL_ORIGIN=https://gitlab.com/rebuilder/bes_shell.git
BES_SHELL_TAG=1.0.17

function _at_exit()
{
  local _rv=$?
  if [[ ${_rv} == 0 ]]; then
    echo success
  else
    echo failed
  fi
}
trap _at_exit EXIT

set -e

# We need a clean tree with no changes
diff=$(git diff)
test -z "${diff}"

git remote add ${BES_SHELL_REMOTE} ${BES_SHELL_ORIGIN} #--no-tags
for dir in bes_shell; do
  if [[ -d ${dir} ]]; then
    # Update subtree for first time
    git subtree pull --prefix=${dir} bes_shell ${BES_SHELL_TAG} --squash -m "Merging ${BES_SHELL_TAG} into ${dir}"
  else
    # Add subtree for first time
    git subtree add --prefix ${dir} bes_shell ${BES_SHELL_TAG} --squash -m "Adding ${BES_SHELL_TAG} into ${dir}"
  fi
done
git remote remove ${BES_SHELL_REMOTE}
