#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.pip.pip_installation_values import pip_installation_values
from bes.system.host import host
from bes.testing.unit_test import unit_test

class test_pip_installation_values(unit_test):

  def test_macos_py27(self):
    piv = pip_installation_values('/tmp/foo', '2.7', system = 'macos')
    self.assert_filename_equal( '/tmp/foo/bin/pip2.7', piv.pip_exe )
    
  def test_windows_py27(self):
    piv = pip_installation_values(r'c:\tmp\foo', '2.7', system = 'windows')
    self.assert_filename_equal( r'c:\tmp\foo\Scripts\pip2.7.exe', piv.pip_exe )
    
if __name__ == '__main__':
  unit_test.main()
