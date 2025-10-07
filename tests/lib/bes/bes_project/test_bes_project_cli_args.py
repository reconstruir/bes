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

class _bes_project_tester(object):

  def __init__(self, ut):
    self._unit_test = ut
    self.tmp_dir = self._unit_test.make_temp_dir()
    self.root_dir = path.join(self.tmp_dir, 'root')

  def make_args(self, command, *extra_args):
    args = [
      'bes_project',
      command,
      '--root-dir', self.root_dir,
    ] + list(extra_args)
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

  def ensure(self, requirements, requirements_dev = None, versions = None):
    requirements_args = [ requirements ]
    if requirements_dev:
      requirements_args.extend([ '--requirements-dev', requirements_dev ])
    versions_args = []
    for version in versions or []:
      versions_args.extend([ '--version', version ])
    return self.run(self.make_args('ensure', *requirements_args, *versions_args))

  def activate_script(self, version, variant = None):
    variant_args = []
    if variant:
      variant_args.extend([ '--variant', variant ])
    return self.run(self.make_args('activate_script', version, *variant_args))
  
  def run(self, args, cwd = None, env = None):
    return self._unit_test.run_program(self._unit_test._program, args, cwd = cwd, env = env)
    
class test_bes_project_cli_args(program_unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip('too slow')
  
  _program = program_unit_test.resolve_program(__file__, '../../../../bin/best.py')

  def test_ensure(self):
    tester = _bes_project_tester(self)
    requirements_content = '''\
# Requests
beautifulsoup4==4.9.3 # https://github.com/waylan/beautifulsoup
    '''
    requirements_tmp = self.make_temp_file(content = requirements_content)
    rv = tester.ensure(requirements_tmp)
    self.assertEqual( 0, rv.exit_code )

  def test_activate_script(self):
    tester = _bes_project_tester(self)
    requirements_content = '''\
# Requests
beautifulsoup4==4.9.3 # https://github.com/waylan/beautifulsoup
    '''
    requirements_tmp = self.make_temp_file(content = requirements_content)
    version = str(python_exe.default_exe_version())
    rv = tester.ensure(requirements_tmp, versions = [ version ])
    self.assertEqual( 0, rv.exit_code )
    rv = tester.activate_script(version)
    self.assertEqual( 0, rv.exit_code )
    expected = path.join(tester.root_dir, version, 'bin/activate')
    self.assertEqual( expected, rv.output )
    
if __name__ == '__main__':
  program_unit_test.main()
