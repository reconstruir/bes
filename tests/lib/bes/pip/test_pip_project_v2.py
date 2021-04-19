#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.pip.pip_exe import pip_exe
from bes.pip.pip_error import pip_error
from bes.pip.pip_installer import pip_installer
from bes.pip.pip_installer_options import pip_installer_options
from bes.pip.pip_installer_tester_v2 import pip_installer_tester_v2
from bes.pip.pip_project_v2 import pip_project_v2
from bes.python.python_testing import python_testing
from bes.fs.file_find import file_find
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_skip import skip_if
from bes.version.software_version import software_version
from bes.testing.unit_test_skip import raise_skip

class test_pip_project_v2(unit_test):

  @classmethod
  def setUpClass(clazz):
    #raise_skip('Not ready')
    pass

  @skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install_invalid_package - no python3 found', warning = True)
  def test_install_invalid_package(self):
    tester = pip_installer_tester_v2(python_testing._PYTHONS.ANY_PYTHON3, 'kiwi', debug = self.DEBUG)
    tester.installer.install('latest', False)
    project = tester.installer._project
    with self.assertRaises(pip_error) as ctx:
      project.install('somethingthatdoesntexistshaha')
    self.assertTrue( 'no matching distribution found for somethingthatdoesntexistshaha' in str(ctx.exception).lower() )

  @skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install_invalid_version - no python3 found', warning = True)
  def test_install_invalid_version(self):
    tester = pip_installer_tester_v2(python_testing._PYTHONS.ANY_PYTHON3, 'kiwi', debug = self.DEBUG)
    tester.installer.install('latest', False)
    project = tester.installer._project
    with self.assertRaises(pip_error) as ctx:
      project.install('pyinstaller', version = '666.666.666.666.666')
    self.assertTrue( 'no matching distribution found for pyinstaller==666.666.666.666.666' in str(ctx.exception).lower() )
    
  @skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install_latest_version - no python3 found', warning = True)
  def test_install_latest_version(self):
    tester = pip_installer_tester_v2(python_testing._PYTHONS.ANY_PYTHON3, 'kiwi', debug = self.DEBUG)
    tester.installer.install('latest', False)
    project = tester.installer._project
    project.install('pyinstaller')
    rv = project.call_program([ 'pyinstaller', '--version' ])
    self.assertEqual( 0, rv.exit_code )
    
  @skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install - no python3 found', warning = True)
  def test_install_specific_version(self):
    tester = pip_installer_tester_v2(python_testing._PYTHONS.ANY_PYTHON3, 'kiwi', debug = self.DEBUG)
    tester.installer.install('latest', False)
    project = tester.installer._project
    project.install('pyinstaller', version = '3.5')
    rv = project.call_program([ 'pyinstaller', '--version' ])
    self.assertEqual( '3.5', rv.stdout.strip() )
    
if __name__ == '__main__':
  unit_test.main()