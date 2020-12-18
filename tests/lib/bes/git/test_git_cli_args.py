#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.git.git import git
from bes.git.git_temp_repo import git_temp_repo
from bes.git.git_unit_test import git_temp_home_func
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.system.env_override import env_override

from bes.testing.program_unit_test import program_unit_test
from bes.git.git_cli_command import git_cli_command
from bes.git.git_cli_options import git_cli_options

class test_git_cli_command(program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '..', '..', '..', '..', 'bin', 'best.py')
  
  @git_temp_home_func()
  def test_bump_tag(self):
    'Just a smoke test bes.git has more test cases for bump_tag'
    content = [
      'file foo.txt "this is foo.txt" 644',
      'file bar.txt "this is bar.txt" 644',
    ]
    r1 = git_temp_repo(content = content, debug = self.DEBUG)
    r2 = r1.make_temp_cloned_repo()
    self.assertEqual( None, r1.greatest_local_tag() )

    args = [
      'git',
      'bump_tag',
      '--root-dir', r1.root,
      '--component', 'revision',
      '--reset-lower',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    r2.pull()
    self.assertEqual( '1.0.0', r2.greatest_local_tag() )

    args = [
      'git',
      'bump_tag',
      '--root-dir', r1.root,
      '--component', 'revision',
      '--reset-lower',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    r2.pull()
    self.assertEqual( '1.0.1', r2.greatest_local_tag() )

    args = [
      'git',
      'bump_tag',
      '--root-dir', r1.root,
      '--component', 'minor',
      '--reset-lower',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    r2.pull()
    self.assertEqual( '1.1.0', r2.greatest_local_tag() )

    args = [
      'git',
      'bump_tag',
      '--root-dir', r1.root,
      '--component', 'major',
      '--reset-lower',
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    r2.pull()
    self.assertEqual( '2.0.0', r2.greatest_local_tag() )

if __name__ == '__main__':
  program_unit_test.main()
