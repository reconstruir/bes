#!/usr/bin/env python
# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.git.git_unit_test import git_temp_home_func
from bes.system.env_override import env_override_temp_home_func

from bes.testing.program_unit_test import program_unit_test

class test_git_identity_cli_args(program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '..', '..', '..', '..', 'bin', 'best.py')
  
  @env_override_temp_home_func()
  def test_git_identity_get_never_set(self):
    args = [
      'git_identity',
      'get',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    self.assertEqual( '', rv.output.strip() )

  @env_override_temp_home_func()
  def test_git_identity_set(self):
    args = [
      'git_identity',
      'set',
      'Foo Bar',
      'foobar@example.com',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)

    args = [
      'git_identity',
      'get',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    self.assertEqual( 'Foo Bar:foobar@example.com', rv.output.strip() )

    args = [
      'git_identity',
      'get',
      '--name',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    self.assertEqual( 'Foo Bar', rv.output.strip() )

    args = [
      'git_identity',
      'get',
      '--email',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    self.assertEqual( 'foobar@example.com', rv.output.strip() )

  @env_override_temp_home_func()
  def xtest_git_identity_ensure(self):
    args = [
      'git_identity',
      'ensure',
      'Foo Bar',
      'foobar@example.com',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)

    args = [
      'git_identity',
      'get',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    self.assertEqual( 'Foo Bar:foobar@example.com', rv.output.strip() )

if __name__ == '__main__':
  program_unit_test.main()
