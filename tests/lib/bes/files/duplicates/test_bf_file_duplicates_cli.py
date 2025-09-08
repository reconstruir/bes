#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.testing.program_unit_test import program_unit_test

class test_bf_file_duplicates_cli(program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '..', '..', '..', '..', '..', 'bin', 'best2.py')

  def test_set_get(self):
    tmp = self.make_temp_file(suffix = '.secret')
    args = [
      'resolve',
      'files',
      '/tmp',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    print(rv.output.strip())
    return
    args = [
      'bf_file_duplicates',
      '--password', 'idunno',
      'get',
      tmp,
      'global',
      'username',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    self.assertEqual('fred', rv.output.strip())
    
if __name__ == '__main__':
  program_unit_test.main()
