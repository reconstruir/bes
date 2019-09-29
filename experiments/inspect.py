#!/usr/bin/env python3

import sys
from bes.testing.framework import unit_test_inspect as UTI

tests = UTI.inspect_file(sys.argv[1])
for test in tests:
  print('TEST: %s - %s' % (test, type(test)))
