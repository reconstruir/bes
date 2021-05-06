#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.python.python_error import python_error
from bes.python.python_testing import python_testing
from bes.python.python_virtual_env import python_virtual_env
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_skip import raise_skip
from bes.testing.unit_test_skip import skip_if
from bes.testing.unit_test_skip import skip_if_not_unix
from bes.testing.unit_test_skip import skip_if_not_windows

class test_pip_installer_v2(unit_test):

  @classmethod
  def setUpClass(clazz):
    pass
    #raise_skip('Not ready')

  @skip_if_not_unix()
  @skip_if(not python_testing._PYTHONS.PYTHON_37, 'test_venv_python_37 - python 3.7 not found', warning = True)
  def test_venv_unix_python_37(self):
    tmp_dir = self.make_temp_dir()
    venv = python_virtual_env(python_testing._PYTHONS.PYTHON_37, tmp_dir)
    expected_exe = path.join(tmp_dir, 'bin', 'python3.7')
    self.assertEqual( expected_exe, venv.python_exe )
    self.assertEqual( expected_exe, venv.installation.python_exe )

  @skip_if_not_windows()
  @skip_if(not python_testing._PYTHONS.PYTHON_27, 'test_venv_python_27 - python 2.7 not found', warning = True)
  def test_venv_windows_python_27(self):
    tmp_dir = self.make_temp_dir()
    with self.assertRaises(python_error) as ctx:
      venv = python_virtual_env(python_testing._PYTHONS.PYTHON_27, tmp_dir)
    self.assertTrue( 'Python version "2.7" not supported'.lower() in str(ctx.exception).lower() )
    
  @skip_if_not_windows()
  @skip_if(not python_testing._PYTHONS.PYTHON_37, 'test_venv_python_37 - python 3.7 not found', warning = True)
  def test_venv_windows_python_37(self):
    tmp_dir = self.make_temp_dir()
    venv = python_virtual_env(python_testing._PYTHONS.PYTHON_37, tmp_dir)
    expected_bin_dir = path.join(tmp_dir, 'Scripts')
    expected_exe = path.join(expected_bin_dir, 'python.exe')
    expected_pip_exe = path.join(expected_bin_dir, 'pip3.7.exe')
    self.assertEqual( expected_exe, venv.python_exe )
    self.assertEqual( expected_exe, venv.installation.python_exe )
    self.assertEqual( '3.7', venv.installation.python_version )
    self.assert_filename_equal( expected_exe, venv.installation.python_exe )
    self.assert_filename_equal( expected_pip_exe, venv.installation.pip_exe )
    self.assert_filename_list_equal( [ expected_bin_dir ], venv.installation.PATH )

  @skip_if_not_windows()
  @skip_if(not python_testing._PYTHONS.PYTHON_38, 'test_venv_python_38 - python 3.8 not found', warning = True)
  def test_venv_windows_python_38(self):
    tmp_dir = self.make_temp_dir()
    venv = python_virtual_env(python_testing._PYTHONS.PYTHON_38, tmp_dir)
    expected_bin_dir = path.join(tmp_dir, 'Scripts')
    expected_exe = path.join(expected_bin_dir, 'python.exe')
    expected_pip_exe = path.join(expected_bin_dir, 'pip3.8.exe')
    self.assertEqual( expected_exe, venv.python_exe )
    self.assertEqual( expected_exe, venv.installation.python_exe )
    self.assertEqual( '3.8', venv.installation.python_version )
    self.assert_filename_equal( expected_exe, venv.installation.python_exe )
    self.assert_filename_equal( expected_pip_exe, venv.installation.pip_exe )
    self.assert_filename_list_equal( [ expected_bin_dir ], venv.installation.PATH )

  @skip_if_not_windows()
  @skip_if(not python_testing._PYTHONS.PYTHON_39, 'test_venv_python_39 - python 3.9 not found', warning = True)
  def test_venv_windows_python_39(self):
    tmp_dir = self.make_temp_dir()
    venv = python_virtual_env(python_testing._PYTHONS.PYTHON_39, tmp_dir)
    expected_bin_dir = path.join(tmp_dir, 'Scripts')
    expected_exe = path.join(expected_bin_dir, 'python.exe')
    expected_pip_exe = path.join(expected_bin_dir, 'pip3.9.exe')
    self.assertEqual( expected_exe, venv.python_exe )
    self.assertEqual( expected_exe, venv.installation.python_exe )
    self.assertEqual( '3.9', venv.installation.python_version )
    self.assert_filename_equal( expected_exe, venv.installation.python_exe )
    self.assert_filename_equal( expected_pip_exe, venv.installation.pip_exe )
    self.assert_filename_list_equal( [ expected_bin_dir ], venv.installation.PATH )
    
if __name__ == '__main__':
  unit_test.main()
