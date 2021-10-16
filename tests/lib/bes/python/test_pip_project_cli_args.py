#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from os import path

from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.python.python_exe import python_exe
from bes.system.system_command import system_command
from bes.system.system_command import system_command
from bes.testing.program_unit_test import program_unit_test
from bes.version.semantic_version import semantic_version

class _pip_project_tester(object):

  def __init__(self, ut, name):
    self._unit_test = ut
    self.name = name
    self.tmp_dir = self._unit_test.make_temp_dir()
    self.root_dir = path.join(self.tmp_dir, 'root')
    self.python_version = str(python_exe.default_exe_version())

  def make_args(self, command, *extra_args):
    args = [
      'pip_project',
      command,
      '--root-dir', self.root_dir,
      '--python-version', self.python_version,
      self.name,
    ] + list(extra_args)
    #print('args={}'.format(args))
    return args

  def root_files(self):
    return file_find.find(self.root_dir)

  def installed(self):
    return self._list_command('installed')

  def outdated(self):
    return self._list_command('outdated')

  def _list_command(self, command):
    tmp = self._unit_test.make_temp_file()
    rv = self._unit_test.run_program(self._unit_test._program,
                                     self.make_args(command, '--style', 'brief', '--output', tmp))
    self._unit_test.assertEqual(0, rv.exit_code)
    return system_command.split_lines(file_util.read(tmp, codec = 'utf-8'))
  
class test_pip_project_cli_args(program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '../../../../bin/best.py')

  def test_init(self):
    tester = _pip_project_tester(self, 'kiwi')
    rv = self.run_program(self._program, tester.make_args('init'))
    self.assertEqual(0, rv.exit_code)

  def test_install(self):
    tester = _pip_project_tester(self, 'kiwi')
    rv = self.run_program(self._program, tester.make_args('init'))
    self.assertEqual(0, rv.exit_code)
    installed1 = tester.installed()

    rv = self.run_program(self._program, tester.make_args('install', 'chardet'))
    self.assertEqual(0, rv.exit_code)
    installed2 = tester.installed()
    
    actual = set(installed2) - set(installed1)
    expected = { 'chardet' }
    self.assertEqual( expected, actual )

  def test_outdated(self):
    tester = _pip_project_tester(self, 'kiwi')
    rv = self.run_program(self._program, tester.make_args('init'))
    self.assertEqual(0, rv.exit_code)

    rv = self.run_program(self._program, tester.make_args('install', 'chardet', '--version', '3.0.4'))
    self.assertEqual(0, rv.exit_code)
    self.assertTrue( 'chardet' in set(tester.outdated()) )

  def xtest_upgrade(self):
    tester = _pip_project_tester(self, 'kiwi')
    rv = self.run_program(self._program, tester.make_args('init'))
    self.assertEqual(0, rv.exit_code)

    old_version = semantic_version('3.0.4')
    
    rv = self.run_program(self._program, tester.make_args('install', 'chardet', '--version', str(old_version)))
    self.assertEqual(0, rv.exit_code)
    #self.assertEqual( { 'chardet' }, set(tester.outdated()) )

    #old_version = semantic_version('3.0.4')
    
if __name__ == '__main__':
  program_unit_test.main()
