#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bat_project.bat_project import bat_project
from bes.bat_project.bat_project_options import bat_project_options
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.uv.uv_exe import uv_exe

class test_bat_project(unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if(not uv_exe.find_or_none(), 'uv not found')

  def _make_project(self, tmp_dir):
    return bat_project(options=bat_project_options(root_dir=tmp_dir,
                                                    name='test',
                                                    debug=self.DEBUG))

  def _make_requirements(self, content=None):
    content = content or 'beautifulsoup4==4.9.3\n'
    return self.make_temp_file(content=content)

  def test_ensure_one_version(self):
    tmp_dir = self.make_temp_dir()
    project = self._make_project(tmp_dir)
    requirements = self._make_requirements()
    project.ensure(['3.13'], requirements)
    self.assertEqual(['3.13'], project.versions)

  def test_ensure_many_versions(self):
    tmp_dir = self.make_temp_dir()
    project = self._make_project(tmp_dir)
    requirements = self._make_requirements()
    project.ensure(['3.11', '3.13'], requirements)
    self.assertEqual(['3.11', '3.13'], sorted(project.versions))

  def test_ensure_remove_one(self):
    tmp_dir = self.make_temp_dir()
    project = self._make_project(tmp_dir)
    requirements = self._make_requirements()
    project.ensure(['3.11', '3.13'], requirements)
    self.assertEqual({'3.11', '3.13'}, set(project.versions))
    project.ensure(['3.13'], requirements)
    self.assertEqual(['3.13'], project.versions)

  def test_ensure_idempotent(self):
    tmp_dir = self.make_temp_dir()
    project = self._make_project(tmp_dir)
    requirements = self._make_requirements()
    project.ensure(['3.13'], requirements)
    project.ensure(['3.13'], requirements)
    self.assertEqual(['3.13'], project.versions)

  def test_versions_empty_before_ensure(self):
    tmp_dir = self.make_temp_dir()
    project = self._make_project(tmp_dir)
    self.assertEqual([], project.versions)

if __name__ == '__main__':
  unit_test.main()
