#!/bin/bash

set -e -x

EGO_BES_UNIT_TESTS=${EGO_BES_UNIT_TESTS:-"*"}
_TESTS="${REBUILD_BUILD_DIR}/tests/${EGO_BES_UNIT_TESTS}"

${_BES_TEST} --verbose --file-ignore-file .bes_test_internal_ignore --dont-hack-env ${_TESTS}
