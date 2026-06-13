#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.uv.uv_exe import uv_exe
from bes.uv.uv_venv import uv_venv

_UV_EXE = uv_exe.find_or_none()

class test_uv_venv(unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if_not(_UV_EXE is not None, 'uv not found')

  def test_is_valid_before_create(self):
    tmp_dir = self.make_temp_dir()
    venv_dir = path.join(tmp_dir, 'venv')
    v = uv_venv(venv_dir, _UV_EXE)
    self.assertFalse(v.is_valid())

  def test_create(self):
    tmp_dir = self.make_temp_dir()
    venv_dir = path.join(tmp_dir, 'venv')
    v = uv_venv(venv_dir, _UV_EXE)
    self.assertFalse(v.is_valid())
    v.create()
    self.assertTrue(v.is_valid())

  def test_create_is_idempotent(self):
    tmp_dir = self.make_temp_dir()
    venv_dir = path.join(tmp_dir, 'venv')
    v = uv_venv(venv_dir, _UV_EXE)
    v.create()
    v.create()
    self.assertTrue(v.is_valid())

  def test_python_exe(self):
    tmp_dir = self.make_temp_dir()
    venv_dir = path.join(tmp_dir, 'venv')
    v = uv_venv(venv_dir, _UV_EXE)
    v.create()
    self.assertTrue(path.isfile(v.python_exe))

  def test_bin_dir(self):
    tmp_dir = self.make_temp_dir()
    venv_dir = path.join(tmp_dir, 'venv')
    v = uv_venv(venv_dir, _UV_EXE)
    v.create()
    self.assertTrue(path.isdir(v.bin_dir))

  def test_site_packages_dir(self):
    tmp_dir = self.make_temp_dir()
    venv_dir = path.join(tmp_dir, 'venv')
    v = uv_venv(venv_dir, _UV_EXE)
    v.create()
    self.assertTrue(path.isdir(v.site_packages_dir))
    self.assertIn('site-packages', v.site_packages_dir)

  def test_root_dir_is_absolute(self):
    tmp_dir = self.make_temp_dir()
    venv_dir = path.join(tmp_dir, 'venv')
    v = uv_venv(venv_dir, _UV_EXE)
    self.assertTrue(path.isabs(v.root_dir))

if __name__ == '__main__':
  unit_test.main()
