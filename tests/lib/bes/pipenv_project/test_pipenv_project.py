#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.pipenv_project.pipenv_project import pipenv_project
from bes.pipenv_project.pipenv_project_options import pipenv_project_options
from bes.pipenv_project.pipenv_project_error import pipenv_project_error

from bes.python.python_testing import python_testing
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip
from bes.fs.file_find import file_find
from bes.testing.unit_test_class_skip import unit_test_class_skip

class test_pipenv_project(unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip('too slow')
  
  @unit_test_function_skip.skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_create - no python3 found', warning = True)
  def test_create(self):
    tmp_dir = self.make_temp_dir()
    options = pipenv_project_options(root_dir = tmp_dir,
                                     debug = self.DEBUG)
    project = pipenv_project(options = options)
    rv = project.call_pipenv([ '--version' ])
    self.assertTrue( rv.stdout.strip().startswith('pipenv, version') )
    rv = project.call_pipenv([ 'graph' ])
    print(rv.stdout)

  @unit_test_function_skip.skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_create - no python3 found', warning = True)
  def xtest_create(self):
    tmp_dir = self.make_temp_dir()
    options = pipenv_project_options(root_dir = tmp_dir,
                                     debug = self.DEBUG)
    project = pipenv_project(options = options)
    rv = project.call_pipenv([ '--version' ])
    self.assertTrue( rv.stdout.strip().startswith('pipenv, version') )
    
if __name__ == '__main__':
  unit_test.main()
