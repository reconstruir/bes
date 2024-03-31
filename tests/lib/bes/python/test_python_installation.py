#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.python.python_installation import python_installation
from bes.python.python_testing import python_testing
from bes.system.host import host
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

def _skip(name, is_system, exe, version):
  return python_testing.skip_if_not(name, is_system, exe, version)

class test_python_installation(unit_test):

  @_skip('test_macos_xcode_38', 'is_macos', python_testing._PYTHONS.PYTHON_38, '3.8')
  def test_macos_xcode_38(self):
    tmp_dir = python_testing.make_temp_fake_python_installation('3.8',
                                                                '19.2.3',
                                                                'xcode',
                                                                system = 'macos',
                                                                debug = self.DEBUG)

    piv = python_installation(path.join(tmp_dir, 'bin/python3'), system = 'macos')
    self.assertEqual( '3.8', piv.python_version )
    self.assert_filename_equal( path.join(tmp_dir, 'bin/python3'), piv.python_exe )
    self.assert_filename_equal( path.join(tmp_dir, 'bin/pip3'), piv.pip_exe )
    self.assert_filename_list_equal( [ path.join(tmp_dir, 'bin') ], piv.PATH )

  @_skip('test_macos_brew_38', 'is_macos', python_testing._PYTHONS.PYTHON_38, '3.8')
  def test_macos_brew_38(self):
    tmp_dir = python_testing.make_temp_fake_python_installation('3.8',
                                                                '21.0.1',
                                                                'brew',
                                                                system = 'macos',
                                                                debug = self.DEBUG)

    piv = python_installation(path.join(tmp_dir, 'bin/python3.8'), system = 'macos')
    self.assertEqual( '3.8', piv.python_version )
    self.assert_filename_equal( path.join(tmp_dir, 'bin/python3.8'), piv.python_exe )
    self.assert_filename_equal( path.join(tmp_dir, 'bin/pip3.8'), piv.pip_exe )
    self.assert_filename_list_equal( [ path.join(tmp_dir, 'bin') ], piv.PATH )
    
  @_skip('test_windows_python_38', 'is_windows', python_testing._PYTHONS.PYTHON_38, '3.8')
  def test_windows_python_38(self):
    tmp_dir = python_testing.make_temp_fake_python_installation('3.8',
                                                                '19.2.3',
                                                                None,
                                                                system = 'windows',
                                                                debug = self.DEBUG)

    piv = python_installation(path.join(tmp_dir, 'python.bat'), system = 'windows')
    self.assertEqual( '3.8', piv.python_version )
    self.assert_filename_equal( path.join(tmp_dir, 'python.bat'), piv.python_exe )
    self.assert_filename_equal( path.join(tmp_dir, 'Scripts', 'pip3.8.bat'), piv.pip_exe )
    self.assert_filename_list_equal( [
      tmp_dir,
      path.join(tmp_dir, 'Scripts'),
    ], piv.PATH )

if __name__ == '__main__':
  unit_test.main()
