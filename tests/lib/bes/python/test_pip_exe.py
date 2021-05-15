#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.file_util import file_util
from bes.pip.pip_exe import pip_exe
from bes.python.python_testing import python_testing
from bes.system.host import host
from bes.testing.unit_test import unit_test

class test_pip_exe(unit_test):

  def test_filename_info_no_version(self):
    fake_exe = python_testing.make_temp_fake_pip('pip', '666.0.1', '2.7')
    version, _ = pip_exe.filename_info(fake_exe)
    self.assertEqual( None, version )

  def test_filename_info_major_version(self):
    fake_exe = python_testing.make_temp_fake_pip('pip2', '666.0.1', '2.7')
    version, _ = pip_exe.filename_info(fake_exe)
    self.assertEqual( '2', version )
  
  def test_filename_info_major_and_minor_version(self):
    fake_exe = python_testing.make_temp_fake_pip('pip2.7', '666.0.1', '2.7')
    version, _ = pip_exe.filename_info(fake_exe)
    self.assertEqual( '2.7', version )

  def test_filename_info_no_version_with_site_packages(self):
    fake_exe = python_testing.make_temp_fake_pip('pip', '666.0.1', '2.7')
    version, _ = pip_exe.filename_info(fake_exe)
    self.assertEqual( None, version )

  def test_filename_info_major_version_with_site_packages(self):
    fake_exe = python_testing.make_temp_fake_pip('pip2', '666.0.1', '2.7')
    version, _ = pip_exe.filename_info(fake_exe)
    self.assertEqual( '2', version )
    
  def test_version_info(self):
    fake_exe = python_testing.make_temp_fake_pip('pip', '666.0.1', '2.7')
    self.assertEqual( ( '666.0.1', '/foo/site-packages/pip', '2.7' ), pip_exe.version_info(fake_exe) )

  def test_version(self):
    fake_exe = python_testing.make_temp_fake_pip('pip', '666.0.1', '2.7')
    self.assertEqual( '666.0.1', pip_exe.version(fake_exe) )

if __name__ == '__main__':
  unit_test.main()
