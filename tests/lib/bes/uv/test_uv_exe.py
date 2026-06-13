#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip
from bes.uv.uv_error import uv_error
from bes.uv.uv_exe import uv_exe
from bes.uv.uv_exe_info import uv_exe_info

_UV_EXE = uv_exe.find_or_none()
_HAVE_UV = _UV_EXE is not None

class test_uv_exe(unit_test):

  @unit_test_function_skip.skip_if(not _HAVE_UV, 'uv not found', warning=True)
  def test_find_or_none(self):
    result = uv_exe.find_or_none()
    self.assertIsNotNone(result)
    self.assertTrue(os.path.isfile(result))

  @unit_test_function_skip.skip_if(not _HAVE_UV, 'uv not found', warning=True)
  def test_find_with_explicit_path(self):
    result = uv_exe.find(explicit_path=_UV_EXE)
    self.assertEqual(_UV_EXE, result)

  def test_find_with_bad_explicit_path(self):
    with self.assertRaises(uv_error):
      uv_exe.find(explicit_path='/nonexistent/path/to/uv')

  @unit_test_function_skip.skip_if(not _HAVE_UV, 'uv not found', warning=True)
  def test_version(self):
    version_string = uv_exe.version(_UV_EXE)
    self.assertIsNotNone(version_string)
    self.assertIsInstance(version_string, str)
    self.assertGreater(len(version_string), 0)
    # version should look like "0.x.y"
    parts = version_string.split('.')
    self.assertGreaterEqual(len(parts), 2)

  @unit_test_function_skip.skip_if(not _HAVE_UV, 'uv not found', warning=True)
  def test_info(self):
    info = uv_exe.info(_UV_EXE)
    self.assertIsInstance(info, uv_exe_info)
    self.assertEqual(_UV_EXE, info.exe_path)
    self.assertIsNotNone(info.version)

  def test_find_uv_env_var(self):
    saved = os.environ.get('UV', None)
    try:
      if _HAVE_UV:
        os.environ['UV'] = _UV_EXE
        result = uv_exe.find_or_none()
        self.assertEqual(_UV_EXE, result)
      else:
        os.environ['UV'] = '/nonexistent/uv'
        result = uv_exe.find_or_none()
        self.assertIsNone(result)
    finally:
      if saved is None:
        os.environ.pop('UV', None)
      else:
        os.environ['UV'] = saved

if __name__ == '__main__':
  unit_test.main()
