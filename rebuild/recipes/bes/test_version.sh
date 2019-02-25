#!/bin/bash

set -e
source ${REBUILD_SHELL_FRAMEWORK_DIR}/bes_shell.sh
set -x

exe=$(which bes_test.py)
version=$( ${exe} --version | awk '{ print $1; }' )

bes_assert "[ ${version} = ${REBUILD_PACKAGE_UPSTREAM_VERSION} ]"
