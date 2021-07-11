#!/bin/bash

./scripts/vmware-run-unit-tests.py --config caca.config poto3 ${1+"$@"}
exit $?
