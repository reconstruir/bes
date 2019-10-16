#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.system.execute import command_line

class test_command_line(unit_test):

  def test_parse_args(self):
    self.assertEqual( [ 'echo', 'foo' ], command_line.parse_args('echo foo') )
    self.assertEqual( [ 'echo', 'foo' ], command_line.parse_args([ 'echo', 'foo' ]) )

if __name__ == "__main__":
  unit_test.main()
