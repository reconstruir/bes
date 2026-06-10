#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.files.bf_file_ops import bf_file_ops
from bes.files.bf_temp_file import bf_temp_file
from bes.archive.archiver import archiver

from bes.testing.program_unit_test import program_unit_test

class test_archive_cli_args(program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '..', '..', '..', '..', 'bin', 'best.py')

if __name__ == '__main__':
  program_unit_test.main()
