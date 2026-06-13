#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.uv.uv_error import uv_error
from bes.uv.uv_exe import uv_exe
from bes.uv.uv_project import uv_project
from bes.uv.uv_project_options import uv_project_options

_UV_EXE = uv_exe.find_or_none()

class test_uv_project(unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip('too slow')

  def _make_project(self, tmp_dir):
    options = uv_project_options(root_dir=tmp_dir, uv_exe=_UV_EXE, debug=self.DEBUG)
    project = uv_project(options=options)
    project.ensure_ready()
    return project

  def test_ensure_ready(self):
    tmp_dir = self.make_temp_dir()
    options = uv_project_options(root_dir=tmp_dir, uv_exe=_UV_EXE, debug=self.DEBUG)
    project = uv_project(options=options)
    self.assertFalse(path.isfile(path.join(tmp_dir, 'pyvenv.cfg')))
    project.ensure_ready()
    self.assertTrue(path.isfile(path.join(tmp_dir, 'pyvenv.cfg')))

  def test_ensure_ready_is_idempotent(self):
    tmp_dir = self.make_temp_dir()
    options = uv_project_options(root_dir=tmp_dir, uv_exe=_UV_EXE, debug=self.DEBUG)
    project = uv_project(options=options)
    project.ensure_ready()
    project.ensure_ready()
    self.assertTrue(path.isfile(path.join(tmp_dir, 'pyvenv.cfg')))

  def test_install_invalid_package(self):
    tmp_dir = self.make_temp_dir()
    project = self._make_project(tmp_dir)
    with self.assertRaises(uv_error):
      project.install('somethingthatdoesnotexistzzz')

  def test_install_latest_version(self):
    tmp_dir = self.make_temp_dir()
    project = self._make_project(tmp_dir)
    project.install('six')
    installed_names = [p.name for p in project.installed()]
    self.assertIn('six', installed_names)

  def test_install_specific_version(self):
    tmp_dir = self.make_temp_dir()
    project = self._make_project(tmp_dir)
    project.install('six', version='1.16.0')
    self.assertEqual('1.16.0', project.version('six'))

  def test_install_invalid_version(self):
    tmp_dir = self.make_temp_dir()
    project = self._make_project(tmp_dir)
    with self.assertRaises(uv_error):
      project.install('six', version='666.666.666')

  def test_installed_returns_sorted_list(self):
    tmp_dir = self.make_temp_dir()
    project = self._make_project(tmp_dir)
    project.install('six')
    project.install('attrs')
    installed = project.installed()
    names = [p.name for p in installed]
    self.assertEqual(sorted(names), names)

  def test_version_unknown_package(self):
    tmp_dir = self.make_temp_dir()
    project = self._make_project(tmp_dir)
    with self.assertRaises(uv_error):
      project.version('no_such_package_xyz')

  def test_needs_upgrade_old_version(self):
    tmp_dir = self.make_temp_dir()
    project = self._make_project(tmp_dir)
    project.install('six', version='1.15.0')
    self.assertTrue(project.needs_upgrade('six'))

  def test_needs_upgrade_latest_version(self):
    tmp_dir = self.make_temp_dir()
    project = self._make_project(tmp_dir)
    project.install('six')
    self.assertFalse(project.needs_upgrade('six'))

  def test_upgrade(self):
    tmp_dir = self.make_temp_dir()
    project = self._make_project(tmp_dir)
    project.install('six', version='1.15.0')
    old_version = project.version('six')
    self.assertEqual('1.15.0', old_version)
    project.upgrade('six')
    new_version = project.version('six')
    self.assertNotEqual(old_version, new_version)

  def test_install_requirements(self):
    tmp_dir = self.make_temp_dir()
    req_file = self.make_temp_file(content='six==1.16.0\n', suffix='.txt')
    project = self._make_project(tmp_dir)
    project.install_requirements(req_file)
    self.assertEqual('1.16.0', project.version('six'))

  def test_install_requirements_checksum_cache(self):
    tmp_dir = self.make_temp_dir()
    req_file = self.make_temp_file(content='six==1.16.0\n', suffix='.txt')
    project = self._make_project(tmp_dir)
    project.install_requirements(req_file)
    checksum_dir = path.join(tmp_dir, '.uv_cache', 'requirements_checksums')
    self.assertTrue(path.isdir(checksum_dir))
    # Call again — should use cached checksum and not re-install
    project.install_requirements(req_file)

  def test_install_requirements_missing_file(self):
    tmp_dir = self.make_temp_dir()
    project = self._make_project(tmp_dir)
    with self.assertRaises(uv_error):
      project.install_requirements('/nonexistent/requirements.txt')

  def test_has_program(self):
    tmp_dir = self.make_temp_dir()
    project = self._make_project(tmp_dir)
    project.install('pip')
    self.assertTrue(project.has_program('pip'))
    self.assertFalse(project.has_program('some_nonexistent_tool_xyz'))

  def test_program_path(self):
    tmp_dir = self.make_temp_dir()
    project = self._make_project(tmp_dir)
    pip_path = project.program_path('pip')
    self.assertTrue(path.isabs(pip_path))

  def test_call_program(self):
    tmp_dir = self.make_temp_dir()
    project = self._make_project(tmp_dir)
    project.install('pip')
    rv = project.call_program(['pip', '--version'])
    self.assertEqual(0, rv.exit_code)

  def test_env_has_virtual_env(self):
    tmp_dir = self.make_temp_dir()
    options = uv_project_options(root_dir=tmp_dir, uv_exe=_UV_EXE, debug=self.DEBUG)
    project = uv_project(options=options)
    self.assertIn('VIRTUAL_ENV', project.env)
    self.assertEqual(tmp_dir, project.env['VIRTUAL_ENV'])

  def test_persistence(self):
    tmp_dir = self.make_temp_dir()
    options = uv_project_options(root_dir=tmp_dir, uv_exe=_UV_EXE, debug=self.DEBUG)
    p1 = uv_project(options=options)
    p1.ensure_ready()
    p1.install('six', version='1.16.0')
    self.assertEqual('1.16.0', p1.version('six'))
    p2 = uv_project(options=options)
    p2.ensure_ready()
    self.assertEqual('1.16.0', p2.version('six'))

if __name__ == '__main__':
  unit_test.main()
