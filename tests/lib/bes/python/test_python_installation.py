#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.python.python_installation import python_installation
from bes.python.python_testing import python_testing
from bes.system.host import host
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

class test_python_installation(unit_test):

  @unit_test_function_skip.skip_if(not host.is_macos(), 'not macos')
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

  @unit_test_function_skip.skip_if(not host.is_macos(), 'not macos')
  def test_macos_system_27(self):
    tmp_dir = python_testing.make_temp_fake_python_installation('2.7',
                                                                None,
                                                                'system',
                                                                system = 'macos',
                                                                debug = self.DEBUG)

    piv = python_installation(path.join(tmp_dir, 'bin/python'), system = 'macos')
    self.assertEqual( '2.7', piv.python_version )
    self.assert_filename_equal( path.join(tmp_dir, 'bin/python2.7'), piv.python_exe )
    self.assert_filename_equal( None, piv.pip_exe )
    self.assert_filename_list_equal( [ path.join(tmp_dir, 'bin') ], piv.PATH )

  @unit_test_function_skip.skip_if(not host.is_macos(), 'not macos')
  def test_macos_brew_37(self):
    tmp_dir = python_testing.make_temp_fake_python_installation('3.7',
                                                                '21.0.1',
                                                                'brew',
                                                                system = 'macos',
                                                                debug = self.DEBUG)

    piv = python_installation(path.join(tmp_dir, 'bin/python3.7'), system = 'macos')
    self.assertEqual( '3.7', piv.python_version )
    self.assert_filename_equal( path.join(tmp_dir, 'bin/python3.7'), piv.python_exe )
    self.assert_filename_equal( path.join(tmp_dir, 'bin/pip3.7'), piv.pip_exe )
    self.assert_filename_list_equal( [ path.join(tmp_dir, 'bin') ], piv.PATH )
    
  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
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

  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_windows_python_27(self):
    tmp_dir = python_testing.make_temp_fake_python_installation('2.7',
                                                                '20.3.4',
                                                                None,
                                                                system = 'windows',
                                                                debug = self.DEBUG)

    piv = python_installation(path.join(tmp_dir, 'python.bat'), system = 'windows')
    self.assertEqual( '2.7', piv.python_version )
    self.assert_filename_equal( path.join(tmp_dir, 'python.bat'), piv.python_exe )
    self.assert_filename_equal( path.join(tmp_dir, 'Scripts', 'pip2.7.bat'), piv.pip_exe )
    
if __name__ == '__main__':
  unit_test.main()
