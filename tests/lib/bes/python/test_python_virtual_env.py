#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path

from bes.system.host import host
from bes.python.python_error import python_error
from bes.python.python_testing import python_testing
from bes.python.python_exe import python_exe
from bes.python.python_virtual_env import python_virtual_env
from bes.testing.unit_test import unit_test

def _skip(name, is_system, exe, version):
  return python_testing.skip_if_not(name, is_system, exe, version)

class test_python_virtual_env(unit_test):

  _test = namedtuple('_test', 'expected_version, actual_version, expected_path, actual_path, expected_exe, actual_exe, expected_pip_exe, actual_pip_exe')
  def _test_unix(self, exe):
    expected_version = python_exe.version(exe)
    tmp_dir = self.make_temp_dir(prefix = f'test_venv_{expected_version}_')
    venv = python_virtual_env(exe, tmp_dir)
    expected_bin_dir = path.join(tmp_dir, 'bin')
    expected_exe = path.join(expected_bin_dir, f'python{expected_version}')
    expected_path = [ expected_bin_dir ]
    actual_path = venv.installation.PATH
    expected_pip_exe = path.join(expected_bin_dir, f'pip{expected_version}')
    actual_exe = venv.installation.python_exe
    actual_pip_exe = venv.installation.pip_exe
    actual_version = python_exe.version(actual_exe)
    return self._test(expected_version, actual_version, expected_path, actual_path,
                      expected_exe, actual_exe, expected_pip_exe, actual_pip_exe)

  def _test_windows(self, exe):
    tmp_dir = self.make_temp_dir()
    expected_version = python_exe.version(exe)
    tmp_dir = self.make_temp_dir(prefix = f'test_venv_{expected_version}_')
    venv = python_virtual_env(exe, tmp_dir)
    expected_bin_dir = path.join(tmp_dir, 'Scripts')
    expected_exe = path.join(expected_bin_dir, 'python.exe')
    expected_pip_exe = path.join(expected_bin_dir, f'pip{expected_version}.exe')
    expected_path = [ expected_bin_dir ]
    actual_path = venv.installation.PATH
    actual_version = python_exe.version(actual_exe)
    return self._test(expected_version, actual_version, expected_path, actual_path,
                      expected_exe, actual_exe, expected_pip_exe, actual_pip_exe)
  
  @_skip('test_venv_unix_38', 'is_unix', python_testing._PYTHONS.PYTHON_38, '3.8')
  def test_venv_unix_38(self):
    t = self._test_unix(python_testing._PYTHONS.PYTHON_38)
    self.assertEqual( t.expected_exe, t.actual_exe )
    self.assertEqual( t.expected_pip_exe, t.actual_pip_exe )
    self.assertEqual( t.expected_version, t.actual_version )
    self.assert_filename_list_equal( t.expected_path, t.actual_path )

  @_skip('test_venv_unix_39', 'is_unix', python_testing._PYTHONS.PYTHON_39, '3.9')
  def test_venv_unix_39(self):
    t = self._test_unix(python_testing._PYTHONS.PYTHON_39)
    self.assertEqual( t.expected_exe, t.actual_exe )
    self.assertEqual( t.expected_pip_exe, t.actual_pip_exe )
    self.assertEqual( t.expected_version, t.actual_version )
    self.assert_filename_list_equal( t.expected_path, t.actual_path )

  @_skip('test_venv_unix_310', 'is_unix', python_testing._PYTHONS.PYTHON_310, '3.10')
  def test_venv_unix_310(self):
    t = self._test_unix(python_testing._PYTHONS.PYTHON_310)
    self.assertEqual( t.expected_exe, t.actual_exe )
    self.assertEqual( t.expected_pip_exe, t.actual_pip_exe )
    self.assertEqual( t.expected_version, t.actual_version )
    self.assert_filename_list_equal( t.expected_path, t.actual_path )

  @_skip('test_venv_unix_311', 'is_unix', python_testing._PYTHONS.PYTHON_311, '3.11')
  def test_venv_unix_311(self):
    t = self._test_unix(python_testing._PYTHONS.PYTHON_311)
    self.assertEqual( t.expected_exe, t.actual_exe )
    self.assertEqual( t.expected_pip_exe, t.actual_pip_exe )
    self.assertEqual( t.expected_version, t.actual_version )
    self.assert_filename_list_equal( t.expected_path, t.actual_path )

  @_skip('test_venv_unix_312', 'is_unix', python_testing._PYTHONS.PYTHON_312, '3.12')
  def test_venv_unix_312(self):
    t = self._test_unix(python_testing._PYTHONS.PYTHON_312)
    self.assertEqual( t.expected_exe, t.actual_exe )
    self.assertEqual( t.expected_pip_exe, t.actual_pip_exe )
    self.assertEqual( t.expected_version, t.actual_version )
    self.assert_filename_list_equal( t.expected_path, t.actual_path )
    
  @_skip('test_venv_unix_313', 'is_unix', python_testing._PYTHONS.PYTHON_313, '3.13')
  def test_venv_unix_313(self):
    t = self._test_unix(python_testing._PYTHONS.PYTHON_313)
    self.assertEqual( t.expected_exe, t.actual_exe )
    self.assertEqual( t.expected_pip_exe, t.actual_pip_exe )
    self.assertEqual( t.expected_version, t.actual_version )
    self.assert_filename_list_equal( t.expected_path, t.actual_path )

  @_skip('test_venv_windows_38', 'is_windows', python_testing._PYTHONS.PYTHON_38, '3.8')
  def test_venv_windows_38(self):
    t = self._test_windows(python_testing._PYTHONS.PYTHON_38)
    self.assertEqual( t.expected_exe, t.actual_exe )
    self.assertEqual( t.expected_pip_exe, t.actual_pip_exe )
    self.assertEqual( t.expected_version, t.actual_version )
    self.assert_filename_list_equal( t.expected_path, t.actual_path )

  @_skip('test_venv_windows_39', 'is_windows', python_testing._PYTHONS.PYTHON_39, '3.9')
  def test_venv_windows_39(self):
    t = self._test_windows(python_testing._PYTHONS.PYTHON_39)
    self.assertEqual( t.expected_exe, t.actual_exe )
    self.assertEqual( t.expected_pip_exe, t.actual_pip_exe )
    self.assertEqual( t.expected_version, t.actual_version )
    self.assert_filename_list_equal( t.expected_path, t.actual_path )

  @_skip('test_venv_windows_310', 'is_windows', python_testing._PYTHONS.PYTHON_310, '3.10')
  def test_venv_windows_310(self):
    t = self._test_windows(python_testing._PYTHONS.PYTHON_310)
    self.assertEqual( t.expected_exe, t.actual_exe )
    self.assertEqual( t.expected_pip_exe, t.actual_pip_exe )
    self.assertEqual( t.expected_version, t.actual_version )
    self.assert_filename_list_equal( t.expected_path, t.actual_path )

  @_skip('test_venv_windows_311', 'is_windows', python_testing._PYTHONS.PYTHON_311, '3.11')
  def test_venv_windows_311(self):
    t = self._test_windows(python_testing._PYTHONS.PYTHON_311)
    self.assertEqual( t.expected_exe, t.actual_exe )
    self.assertEqual( t.expected_pip_exe, t.actual_pip_exe )
    self.assertEqual( t.expected_version, t.actual_version )
    self.assert_filename_list_equal( t.expected_path, t.actual_path )

  @_skip('test_venv_windows_312', 'is_windows', python_testing._PYTHONS.PYTHON_312, '3.12')
  def test_venv_windows_312(self):
    t = self._test_windows(python_testing._PYTHONS.PYTHON_312)
    self.assertEqual( t.expected_exe, t.actual_exe )
    self.assertEqual( t.expected_pip_exe, t.actual_pip_exe )
    self.assertEqual( t.expected_version, t.actual_version )
    self.assert_filename_list_equal( t.expected_path, t.actual_path )
    
  @_skip('test_venv_windows_313', 'is_windows', python_testing._PYTHONS.PYTHON_313, '3.13')
  def test_venv_windows_313(self):
    t = self._test_windows(python_testing._PYTHONS.PYTHON_313)
    self.assertEqual( t.expected_exe, t.actual_exe )
    self.assertEqual( t.expected_pip_exe, t.actual_pip_exe )
    self.assertEqual( t.expected_version, t.actual_version )
    self.assert_filename_list_equal( t.expected_path, t.actual_path )
    
if __name__ == '__main__':
  unit_test.main()
