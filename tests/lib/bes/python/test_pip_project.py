#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.file_find import file_find
from bes.python.pip_error import pip_error
from bes.python.pip_exe import pip_exe
from bes.python.pip_installer_options import pip_installer_options
from bes.python.pip_installer_tester import pip_installer_tester
from bes.python.pip_project import pip_project
from bes.python.pip_project_options import pip_project_options
from bes.python.python_testing import python_testing
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip
from bes.version.semantic_version import semantic_version

class test_pip_project(unit_test):

  @unit_test_function_skip.skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install_invalid_package - no python3 found', warning = True)
  def test_install_invalid_package(self):
    tmp_dir = self.make_temp_dir()
    options = pip_project_options(root_dir = tmp_dir,
                                  python_exe = python_testing._PYTHONS.ANY_PYTHON3,
                                  debug = self.DEBUG)
    project = pip_project(options = options)
    with self.assertRaises(pip_error) as ctx:
      project.install('somethingthatdoesntexistshaha')
    self.assertTrue( 'no matching distribution found for somethingthatdoesntexistshaha' in str(ctx.exception).lower() )

  @unit_test_function_skip.skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install_invalid_version - no python3 found', warning = True)
  def test_install_invalid_version(self):
    tmp_dir = self.make_temp_dir()
    options = pip_project_options(root_dir = tmp_dir,
                                  python_exe = python_testing._PYTHONS.ANY_PYTHON3,
                                  debug = self.DEBUG)
    project = pip_project(options = options)
    with self.assertRaises(pip_error) as ctx:
      project.install('pyinstaller', version = '666.666.666.666.666')
    self.assertTrue( 'no matching distribution found for pyinstaller==666.666.666.666.666' in str(ctx.exception).lower() )
    
  @unit_test_function_skip.skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install_latest_version - no python3 found', warning = True)
  def test_install_latest_version(self):
    tmp_dir = self.make_temp_dir()
    options = pip_project_options(root_dir = tmp_dir,
                                  python_exe = python_testing._PYTHONS.ANY_PYTHON3,
                                  debug = self.DEBUG)
    project = pip_project(options = options)
    project.install('pyinstaller')
    rv = project.call_program([ 'pyinstaller', '--version' ])
    self.assertEqual( 0, rv.exit_code )
    
  @unit_test_function_skip.skip_if(not python_testing._PYTHONS.PYTHON_311, 'test_install - no python3 found', warning = True)
  def test_install_specific_version_py311(self):
    tmp_dir = self.make_temp_dir()
    options = pip_project_options(root_dir = tmp_dir,
                                  python_exe = python_testing._PYTHONS.PYTHON_311,
                                  debug = self.DEBUG)
    project = pip_project(options = options)
    project.install('pyinstaller', version = '6.9.0')
    rv = project.call_program([ 'pyinstaller', '--version' ])
    self.assertEqual( '6.9.0', rv.stdout.strip() )
    self.assertEqual( '6.9.0', project.version('pyinstaller') )
    self.assertTrue( project.needs_upgrade('pyinstaller') )

  @unit_test_function_skip.skip_if(not python_testing._PYTHONS.PYTHON_311, 'test_upgrade - no python3.11 found', warning = True)
  def test_upgrade(self):
    tmp_dir = self.make_temp_dir()
    options = pip_project_options(root_dir = tmp_dir,
                                  python_exe = python_testing._PYTHONS.PYTHON_311,
                                  debug = self.DEBUG)
    project = pip_project(options = options)
    project.install('pyinstaller', version = '6.9.0')
    rv = project.call_program([ 'pyinstaller', '--version' ])
    old_version = semantic_version(project.version('pyinstaller'))
    self.assertEqual( '6.9.0', old_version )
    project.upgrade('pyinstaller')
    new_version = semantic_version(project.version('pyinstaller'))
    self.assertTrue( new_version > old_version )

  @unit_test_function_skip.skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install - no python3 found', warning = True)
  def test_persistence(self):
    tmp_dir = self.make_temp_dir()
    options = pip_project_options(root_dir = tmp_dir,
                                  python_exe = python_testing._PYTHONS.ANY_PYTHON3,
                                  debug = self.DEBUG)
    p1 = pip_project(options = options)
    p1.install('pyinstaller', version = '6.10.0')
    rv = p1.call_program([ 'pyinstaller', '--version' ])
    self.assertEqual( '6.10.0', p1.version('pyinstaller') )
    p2 = pip_project(options = options)
    p2.install('pyinstaller', version = '6.10.0')
    rv = p2.call_program([ 'pyinstaller', '--version' ])
    self.assertEqual( '6.10.0', p2.version('pyinstaller') )
    
if __name__ == '__main__':
  unit_test.main()
