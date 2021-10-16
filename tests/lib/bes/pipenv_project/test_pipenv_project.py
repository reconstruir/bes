#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.python.pip_exe import pip_exe
from bes.python.pip_error import pip_error
from bes.python.pip_installer_options import pip_installer_options
from bes.python.pip_installer_tester import pip_installer_tester
from bes.python.pip_project import pip_project
from bes.python.python_testing import python_testing
from bes.fs.file_find import file_find
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_skip import skip_if
from bes.version.semantic_version import semantic_version
from bes.testing.unit_test_skip import raise_skip

class test_pipenv_project(unit_test):

  @classmethod
  def setUpClass(clazz):
    #raise_skip('Not ready')
    pass

  @skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install_latest_version - no python3 found', warning = True)
  def xtest_install_latest_version(self):
    tmp_dir = self.make_temp_dir()
    options = pip_project_options(root_dir = tmp_dir,
                                  python_exe = python_testing._PYTHONS.ANY_PYTHON3,
                                  debug = self.DEBUG)
    project = pip_project('kiwi', options = options)
    project.install('pyinstaller')
    rv = project.call_program([ 'pyinstaller', '--version' ])
    self.assertEqual( 0, rv.exit_code )
    
if __name__ == '__main__':
  unit_test.main()
