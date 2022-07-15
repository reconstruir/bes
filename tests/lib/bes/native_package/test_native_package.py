#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.native_package.native_package import native_package
from bes.testing.unit_test_function_skip import unit_test_function_skip
from bes.system.host import host
from bes.testing.unit_test_class_skip import unit_test_class_skip

class test_native_package(unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if_not_macos()

  def test_installed_packages(self):
    np = native_package()
    self.assertTrue( len(np.installed_packages()) > 0 )

  @unit_test_function_skip.skip_if(not host.is_macos(), 'not macos')
  def test_package_manifest_macos(self):
    np = native_package()
    manifest = np.package_files(self._macos_example_pkg())
    self.assertTrue( len(manifest) > 0 )

  @unit_test_function_skip.skip_if(not host.is_macos(), 'not macos')
  def test_package_files_macos(self):
    np = native_package()
    files = np.package_files(self._macos_example_pkg())
    self.assertTrue( len(files) > 0 )

  @unit_test_function_skip.skip_if(not host.is_macos(), 'not macos')
  def test_package_info_macos(self):
    np = native_package()
    info = np.package_info(self._macos_example_pkg())
    self.assertTrue( len(info) > 0 )
    
  @unit_test_function_skip.skip_if(not host.is_macos(), 'not macos')
  def test_is_installed_macos(self):
    np = native_package()
    self.assertFalse( np.is_installed('bash') )
    self.assertTrue( np.is_installed(self._macos_example_pkg()) )
  
  @unit_test_function_skip.skip_if(not host.is_linux(), 'not linux')
  def test_is_installed_linux(self):
    np = native_package()
    self.assertTrue( np.is_installed('bash') )
    self.assertFalse( np.is_installed('foosomethingnottherelikely') )

  @unit_test_function_skip.skip_if(not host.is_macos(), 'not macos')
  def test_owner_macos(self):
    np = native_package()
    pkg = self._macos_example_pkg()
    manifest = np.package_files(pkg)
    self.assertEqual( pkg, np.owner(manifest[0]) )
    
  @unit_test_function_skip.skip_if(not host.is_linux(), 'not linux')
  def test_owner_linux(self):
    np = native_package()
    self.assertEqual( 'coreutils', np.owner('/bin/ls') )
    self.assertEqual( 'bash', np.owner('/bin/bash') )
  
  def test_installed_packages(self):
    np = native_package()
    self.assertTrue( len(np.installed_packages()) > 0 )

  @classmethod
  def _macos_example_pkg(clazz):
    if host.CODENAME in ( 'big_sur', ):
      return 'com.apple.files.data-template'
    else:
      return 'com.apple.pkg.Core'
    
if __name__ == '__main__':
  unit_test.main()
