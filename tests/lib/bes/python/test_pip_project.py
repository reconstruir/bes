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
from bes.version.software_version import software_version
from bes.testing.unit_test_skip import raise_skip

class test_pip_project(unit_test):

  @classmethod
  def setUpClass(clazz):
    #raise_skip('Not ready')
    pass

  @skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install_invalid_package - no python3 found', warning = True)
  def test_install_invalid_package(self):
    tmp_dir = self.make_temp_dir()
    project = pip_project('kiwi', tmp_dir, python_testing._PYTHONS.ANY_PYTHON3, debug = self.DEBUG)
    with self.assertRaises(pip_error) as ctx:
      project.install('somethingthatdoesntexistshaha')
    self.assertTrue( 'no matching distribution found for somethingthatdoesntexistshaha' in str(ctx.exception).lower() )

  @skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install_invalid_version - no python3 found', warning = True)
  def test_install_invalid_version(self):
    tmp_dir = self.make_temp_dir()
    project = pip_project('kiwi', tmp_dir, python_testing._PYTHONS.ANY_PYTHON3, debug = self.DEBUG)
    with self.assertRaises(pip_error) as ctx:
      project.install('pyinstaller', version = '666.666.666.666.666')
    print('ex={}'.format(str(ctx.exception).lower()))
    self.assertTrue( 'no matching distribution found for pyinstaller==666.666.666.666.666' in str(ctx.exception).lower() )
    
  @skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install_latest_version - no python3 found', warning = True)
  def test_install_latest_version(self):
    tmp_dir = self.make_temp_dir()
    project = pip_project('kiwi', tmp_dir, python_testing._PYTHONS.ANY_PYTHON3, debug = self.DEBUG)
    project.install('pyinstaller')
    rv = project.call_program([ 'pyinstaller', '--version' ])
    self.assertEqual( 0, rv.exit_code )
    
  @skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install - no python3 found', warning = True)
  def test_install_specific_version(self):
    tmp_dir = self.make_temp_dir()
    project = pip_project('kiwi', tmp_dir, python_testing._PYTHONS.ANY_PYTHON3, debug = self.DEBUG)
    project.install('pyinstaller', version = '3.5')
    rv = project.call_program([ 'pyinstaller', '--version' ])
    self.assertEqual( '3.5', rv.stdout.strip() )
    
if __name__ == '__main__':
  unit_test.main()
