#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.pip.pip_exe import pip_exe
from bes.pip.pip_installer import pip_installer
from bes.pip.pip_installer_options import pip_installer_options
from bes.pip.pip_installer_tester import pip_installer_tester
from bes.pip.pip_project import pip_project
from bes.python.python_testing import python_testing
from bes.fs.file_find import file_find
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_skip import skip_if
from bes.version.software_version import software_version
from bes.testing.unit_test_skip import raise_skip

class test_pip_project(unit_test):

  @classmethod
  def setUpClass(clazz):
    raise_skip('Not ready')
    pass
  
  @skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install - no python3 found', warning = True)
  def test_install(self):
    tester = pip_installer_tester(python_testing._PYTHONS.ANY_PYTHON3, 'kiwi', debug = True) #self.DEBUG)
    tester.installer.install('latest', False)
    project = tester.installer._project
    project.install('pyinstaller', version = '4.2')
#    files = file_find.find(project.project_dir)
#    for f in files:
#      print('FILE: {}'.format(f))
    rv = project.call_program([ 'pyinstaller', '--version' ])
    self.assertEqual( '4.2', rv.stdout.strip() )
    
if __name__ == '__main__':
  unit_test.main()
