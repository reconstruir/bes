#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# A script to run python unit tests.  Depends on bes which as bit of a chicken-and-egg
# problem when unit testing bes itself.  Use the standalone bes_test version to avoid
# the issue.
from bes.testing.bes_test_runner import main

if __name__ == '__main__':
  raise SystemExit(main())
