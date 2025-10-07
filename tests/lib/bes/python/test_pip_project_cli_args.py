#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from os import path

from bes.common.json_util import json_util
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.python.python_exe import python_exe
from bes.system.system_command import system_command
from bes.system.system_command import system_command
from bes.testing.program_unit_test import program_unit_test
from bes.version.semantic_version import semantic_version
from bes.testing.unit_test_class_skip import unit_test_class_skip

class _pip_project_tester(object):

  def __init__(self, ut):
    self._unit_test = ut
    self.tmp_dir = self._unit_test.make_temp_dir()
    self.root_dir = path.join(self.tmp_dir, 'root')
    self.python_version = str(python_exe.default_exe_version())

  def make_args(self, command, *extra_args):
    args = [
      'pip_project',
      command,
      '--root-dir', self.root_dir,
      '--python-version', self.python_version,
    ] + list(extra_args)
    #print('args={}'.format(args))
    return args

  def root_files(self):
    return file_find.find(self.root_dir)

  def installed(self):
    return self._list_command('installed')

  def outdated(self):
    return self._list_command('outdated')

  def installed_json(self):
    return self._json_command('installed')

  def installed_dict(self):
    result = {}
    for item in self.installed_json():
      result[item['name']] = item['version']
    return result
  
  def _list_command(self, command):
    tmp = self._unit_test.make_temp_file()
    rv = self.run(self.make_args(command, '--style', 'brief', '--output', tmp))
    self._unit_test.assertEqual( 0, rv.exit_code )
    return system_command.split_lines(file_util.read(tmp, codec = 'utf-8'))

  def _json_command(self, command):
    tmp = self._unit_test.make_temp_file()
    rv = self.run(self.make_args(command, '--style', 'json', '--output', tmp))
    self._unit_test.assertEqual( 0, rv.exit_code )
    return json_util.read_file(tmp)

  def create(self):
    return self.run(self.make_args('create'))

  def run(self, args, cwd = None, env = None):
    return self._unit_test.run_program(self._unit_test._program, args, cwd = cwd, env = env)
    
class test_pip_project_cli_args(program_unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip('too slow')
  
  _program = program_unit_test.resolve_program(__file__, '../../../../bin/best.py')

  def test_create(self):
    tester = _pip_project_tester(self)
    rv = tester.create()
    self.assertEqual( 0, rv.exit_code )

  def test_install(self):
    tester = _pip_project_tester(self)
    rv = tester.create()
    self.assertEqual( 0, rv.exit_code )
    installed1 = tester.installed()

    rv = self.run_program(self._program, tester.make_args('install', 'chardet'))
    self.assertEqual( 0, rv.exit_code )
    installed2 = tester.installed()
    
    actual = set(installed2) - set(installed1)
    expected = { 'chardet' }
    self.assertEqual( expected, actual )

  def test_outdated(self):
    tester = _pip_project_tester(self)
    rv = tester.create()
    self.assertEqual( 0, rv.exit_code )

    rv = self.run_program(self._program, tester.make_args('install', 'chardet', '--version', '3.0.4'))
    self.assertEqual( 0, rv.exit_code )
    self.assertTrue( 'chardet' in set(tester.outdated()) )
    
  def test_upgrade_one_package(self):
    tester = _pip_project_tester(self)
    rv = tester.create()
    self.assertEqual( 0, rv.exit_code )

    old_version = semantic_version('3.0.4')
    
    rv = self.run_program(self._program, tester.make_args('install', 'chardet', '--version', str(old_version)))
    self.assertEqual( 0, rv.exit_code )

    installed_before = tester.installed_dict()
    self.assertEqual( str(old_version), installed_before['chardet'] )
    
    rv = self.run_program(self._program, tester.make_args('upgrade', 'chardet'))
    self.assertEqual( 0, rv.exit_code )

    installed_after = tester.installed_dict()
    new_version = semantic_version(installed_after['chardet'])
    self.assertTrue( new_version > old_version )

  def test_upgrade_many_packages(self):
    requirements_content = '''\
idna == 2.7
chardet == 3.0.4
certifi == 2021.5.30
'''
    tmp_requirements = self.make_temp_file(content = requirements_content)
    
    tester = _pip_project_tester(self)
    rv = tester.create()
    self.assertEqual( 0, rv.exit_code )

    rv = self.run_program(self._program, tester.make_args('install_requirements', tmp_requirements))
    self.assertEqual( 0, rv.exit_code )
    installed_before = tester.installed_dict()
    self.assertEqual( '2.7', installed_before['idna'] )
    self.assertEqual( '3.0.4', installed_before['chardet'] )
    self.assertEqual( '2021.5.30', installed_before['certifi'] )

    rv = self.run_program(self._program, tester.make_args('upgrade', 'idna', 'chardet', 'certifi'))
    self.assertEqual( 0, rv.exit_code )
    installed_after = tester.installed_dict()
    self.assertTrue( semantic_version(installed_after['idna']) > semantic_version('2.7') )
    self.assertTrue( semantic_version(installed_after['chardet']) > semantic_version('3.0.4') )
    self.assertTrue( semantic_version(installed_after['certifi']) > semantic_version('2021.5.30') )
    
  def test_install_requirements(self):
    requirements_content = '''\
idna == 2.7
chardet == 3.0.4
certifi == 2021.5.30
'''
    tmp_requirements = self.make_temp_file(content = requirements_content)
    
    tester = _pip_project_tester(self)
    rv = tester.create()
    self.assertEqual( 0, rv.exit_code )

    rv = self.run_program(self._program, tester.make_args('install_requirements', tmp_requirements))
    self.assertEqual( 0, rv.exit_code )
    installed = tester.installed_dict()
    self.assertEqual( '2.7', installed['idna'] )
    self.assertEqual( '3.0.4', installed['chardet'] )
    self.assertEqual( '2021.5.30', installed['certifi'] )
    
if __name__ == '__main__':
  program_unit_test.main()
