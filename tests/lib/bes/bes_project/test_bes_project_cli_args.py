#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.files.bf_file_ops import bf_file_ops
from bes.system.system_command import system_command
from bes.testing.program_unit_test import program_unit_test
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
      '--name', 'test',
    ] + list(extra_args)
    return args

  def ensure(self, requirements, requirements_dev=None, versions=None):
    requirements_args = [requirements]
    if requirements_dev:
      requirements_args.extend(['--requirements-dev', requirements_dev])
    versions_args = []
    for version in versions or []:
      versions_args.extend(['--version', version])
    return self.run(self.make_args('ensure', *requirements_args, *versions_args))

  def activate_script(self, version, variant=None):
    variant_args = []
    if variant:
      variant_args.extend(['--variant', variant])
    return self.run(self.make_args('activate_script', version, *variant_args))

  def run(self, args, cwd=None, env=None):
    return self._unit_test.run_program(self._unit_test._program, args, cwd=cwd, env=env)

class test_bes_project_cli_args(program_unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip('too slow')

  _program = program_unit_test.resolve_program(__file__, '../../../../bin/best.py')

  def test_ensure(self):
    tester = _bes_project_tester(self)
    requirements_tmp = self.make_temp_file(content='beautifulsoup4==4.9.3\n')
    rv = tester.ensure(requirements_tmp, versions=['3.13'])
    self.assertEqual(0, rv.exit_code)

  def test_activate_script(self):
    tester = _bes_project_tester(self)
    requirements_tmp = self.make_temp_file(content='beautifulsoup4==4.9.3\n')
    rv = tester.ensure(requirements_tmp, versions=['3.13'])
    self.assertEqual(0, rv.exit_code)
    rv = tester.activate_script('3.13')
    self.assertEqual(0, rv.exit_code)
    expected = path.join(tester.root_dir, 'projects', 'test', '3.13', 'bin', 'activate')
    self.assertEqual(expected, rv.output)

if __name__ == '__main__':
  program_unit_test.main()
