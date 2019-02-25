#!/bin/bash

set -e

echo COMMAND: $(which bes_test) --verbose --no-env-deps --file-ignore-file .bes_test_internal_ignore ${REBUILD_RECIPE_DIR}/reb-bes_test-test-case.py
$(which bes_test) --verbose --no-env-deps --file-ignore-file .bes_test_internal_ignore ${REBUILD_RECIPE_DIR}/reb-bes_test-test-case.py
