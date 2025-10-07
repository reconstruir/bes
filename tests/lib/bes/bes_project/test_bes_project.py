#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.file_find import file_find
from bes.python.python_exe import python_exe
from bes.bes_project.bes_project import bes_project
from bes.bes_project.bes_project_options import bes_project_options
from bes.python.python_testing import python_testing
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.version.semantic_version import semantic_version
from bes.system.host import host

class test_bes_project(unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip('too slow')
  
  @unit_test_function_skip.skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_ensure_one_version - no python3 found', warning = True)
  def test_ensure_one_version(self):
    tmp_dir = self.make_temp_dir()
    options = bes_project_options(root_dir = tmp_dir,
                                  debug = self.DEBUG)
    project = bes_project(options = options)
    version = python_exe.default_exe_version()
    requirements_content = '''\
beautifulsoup4==4.9.3 # https://github.com/waylan/beautifulsoup
    '''
    requirements_tmp = self.make_temp_file(content = requirements_content)
    project.ensure([ str(version) ], requirements_tmp)
    self.assertEqual( [ version ], project.versions )
    
  @unit_test_function_skip.skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_ensure_many_version - no python3 found', warning = True)
  def test_ensure_many_version(self):
    tmp_dir = self.make_temp_dir()
    options = bes_project_options(root_dir = tmp_dir,
                                  debug = self.DEBUG)
    project = bes_project(options = options)
    versions = self._available_versions()
    requirements_content = '''\
beautifulsoup4==4.9.3 # https://github.com/waylan/beautifulsoup
    '''
    requirements_tmp = self.make_temp_file(content = requirements_content)
    project.ensure(versions, requirements_tmp)
    print('        versions: {} - {}'.format(versions, type(versions)))
    print('project.versions: {} - {}'.format(versions, type(project.versions)))
    self.assertEqual( set(versions), set(project.versions) )
    
  @unit_test_function_skip.skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_ensure_remove_one - no python3 found', warning = True)
  def test_ensure_remove_one(self):
    tmp_dir = self.make_temp_dir()
    options = bes_project_options(root_dir = tmp_dir,
                                  debug = self.DEBUG)
    project = bes_project(options = options)
    versions = self._available_versions()
    requirements_content = '''\
beautifulsoup4==4.9.3 # https://github.com/waylan/beautifulsoup
    '''
    requirements_tmp = self.make_temp_file(content = requirements_content)
    project.ensure(versions, requirements_tmp)
    self.assertEqual( set(versions), set(project.versions) )
    only_version = python_exe.default_exe_version()
    project.ensure([ str(only_version) ], requirements_tmp)
    self.assertEqual( [ only_version ], project.versions )

  @classmethod
  def _available_versions(clazz):
    versions = python_exe.available_versions()
    if '2.7' in versions:
      versions.remove('2.7')
    if host.is_linux() and '3.9' in versions:
      versions.remove('3.9')
    return versions

if __name__ == '__main__':
  unit_test.main()
