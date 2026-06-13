#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.uv.uv_exe import uv_exe
from bes.uv_installer.uv_installer import uv_installer
from bes.uv_installer.uv_installer_options import uv_installer_options

_UV_EXE = uv_exe.find_or_none()
_HAVE_UV = _UV_EXE is not None

class test_uv_installer(unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if_not(_HAVE_UV, 'uv not found')

  def _make_installer(self, **kwargs):
    options = uv_installer_options(**kwargs)
    return uv_installer(options)

  def test_is_installed(self):
    installer = self._make_installer()
    self.assertTrue(installer.is_installed())

  def test_installed_version(self):
    installer = self._make_installer()
    version = installer.installed_version()
    self.assertIsNotNone(version)
    self.assertIsInstance(version, str)
    parts = version.split('.')
    self.assertGreaterEqual(len(parts), 2)

  def test_exe_path(self):
    installer = self._make_installer()
    exe = installer.exe_path()
    self.assertIsNotNone(exe)
    self.assertTrue(path.isfile(exe))

  def test_is_installed_custom_dir(self):
    tmp_dir = self.make_temp_dir()
    installer = self._make_installer(install_dir=tmp_dir)
    self.assertFalse(installer.is_installed())

  def test_exe_path_none_when_not_installed(self):
    tmp_dir = self.make_temp_dir()
    installer = self._make_installer(install_dir=tmp_dir)
    self.assertIsNone(installer.exe_path())

  def test_installed_version_none_when_not_installed(self):
    tmp_dir = self.make_temp_dir()
    installer = self._make_installer(install_dir=tmp_dir)
    self.assertIsNone(installer.installed_version())

class test_uv_installer_install_uninstall(unit_test):
  'Slow tests that actually install and remove uv.'

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip('too slow')

  def test_install_and_uninstall(self):
    tmp_dir = self.make_temp_dir()
    options = uv_installer_options(install_dir=tmp_dir, verbose=self.VERBOSE)
    installer = uv_installer(options)
    self.assertFalse(installer.is_installed())
    installer.install()
    self.assertTrue(installer.is_installed())
    exe = installer.exe_path()
    self.assertIsNotNone(exe)
    self.assertTrue(path.isfile(exe))
    version = installer.installed_version()
    self.assertIsNotNone(version)
    installer.uninstall()
    self.assertFalse(installer.is_installed())

  def test_install_specific_version(self):
    tmp_dir = self.make_temp_dir()
    options = uv_installer_options(install_dir=tmp_dir, verbose=self.VERBOSE)
    installer = uv_installer(options)
    installer.install(version='0.4.0')
    self.assertEqual('0.4.0', installer.installed_version())
    installer.uninstall()

  def test_dry_run_install(self):
    tmp_dir = self.make_temp_dir()
    options = uv_installer_options(install_dir=tmp_dir, dry_run=True)
    installer = uv_installer(options)
    installer.install()
    self.assertFalse(installer.is_installed())

if __name__ == '__main__':
  unit_test.main()
