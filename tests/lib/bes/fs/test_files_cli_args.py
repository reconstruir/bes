#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.testing.program_unit_test import program_unit_test

class test_files_cli_args(program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '../../../../bin/best.py')

  def test_fixme(self):
    pass

if __name__ == '__main__':
  program_unit_test.main()
