#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.file_util import file_util
from bes.system.env_override import env_override
from bes.system.host import host
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_skip import skip_if

from bes.python.python_exe import python_exe
from bes.python.python_error import python_error

class test_python_exe(unit_test):

  def test_full_version(self):
    fake_exe = self._make_temp_fake_python('python', 'Python', '2.7.666')
    self.assertEqual( '2.7.666', python_exe.full_version(fake_exe) )

  def test_version(self):
    fake_exe = self._make_temp_fake_python('python', 'Python', '2.7.666')
    self.assertEqual( '2.7', python_exe.version(fake_exe) )

  def test_find_version(self):
    fake_exe = self._make_temp_fake_python('python6.7', 'Python', '6.7.666')
    with env_override(env = { 'PATH': path.dirname(fake_exe) }) as env:
      self.assertEqual( fake_exe, python_exe.find_version('6.7') )

  def test_find_full_version(self):
    fake_exe = self._make_temp_fake_python('python6.7', 'Python', '6.7.666')
    with env_override(env = { 'PATH': path.dirname(fake_exe) }) as env:
      self.assertEqual( fake_exe, python_exe.find_full_version('6.7.666') )

  def test_has_version(self):
    fake_exe = self._make_temp_fake_python('python6.7', 'Python', '6.7.666')
    with env_override(env = { 'PATH': path.dirname(fake_exe) }) as env:
      self.assertTrue( python_exe.has_version('6.7') )
      self.assertFalse( python_exe.has_version('9.8') )
      
  def test_has_full_version(self):
    fake_exe = self._make_temp_fake_python('python6.7', 'Python', '6.7.666')
    with env_override(env = { 'PATH': path.dirname(fake_exe) }) as env:
      self.assertTrue( python_exe.has_full_version('6.7.666') )
      self.assertFalse( python_exe.has_full_version('6.7.667') )

  def test_check_exe_success(self):
    fake_exe = self._make_temp_fake_python('python6.7', 'Python', '6.7.666')
    self.assertEqual( '6.7.666', python_exe.check_exe(fake_exe) )

  @skip_if(not host.is_unix(), 'not unix')
  def test_check_exe_not_executable(self):
    fake_exe = self._make_temp_fake_python('python6.7', 'Python', '6.7.666', mode = 0o0600)
    with self.assertRaises(python_error) as ctx:
      python_exe.check_exe(fake_exe)
    self.assertTrue( 'not a valid executable' in str(ctx.exception) )
    
  def test_check_exe_not_abs(self):
    with self.assertRaises(python_error) as ctx:
      python_exe.check_exe('python6.7')
    self.assertTrue( 'not an absolute path' in str(ctx.exception) )
    
  def test_check_exe_invalid_name(self):
    fake_exe = self._make_temp_fake_python('python6.7', 'awk', '6.7.666')
    with self.assertRaises(python_error) as ctx:
      python_exe.check_exe(fake_exe)
    self.assertTrue( 'not a valid python name' in str(ctx.exception) )

  def _make_temp_fake_python(self, filename, name, version, mode = 0o0755):
    if host.is_unix():
      return self._make_temp_fake_python_unix(filename, name, version, mode = mode)
    elif host.is_windows():
      return self._make_temp_fake_python_windows(filename, name, version, mode = mode)
    else:
      host.raise_unsupported_system()

  def _make_temp_fake_python_unix(self, filename, name, version, mode = 0o0755):
    tmp_dir = self.make_temp_dir()
    tmp_exe = path.join(tmp_dir, filename)
    content = '''\
#!/bin/bash
echo {name} {version} 1>&2
exit 0
'''.format(name = name, version = version)
    file_util.save(tmp_exe, content = content, mode = mode)
    return tmp_exe

  def _make_temp_fake_python_windows(self, filename, name, version, mode = 0o0755):
    tmp_dir = self.make_temp_dir()
    assert not filename.endswith('.bat')
    filename = filename + '.bat'
    tmp_exe = path.join(tmp_dir, filename)
    content = '''\
@echo off
echo {name} {version}
exit /b 0
'''.format(name = name, version = version)
    file_util.save(tmp_exe, content = content, mode = mode)
    return tmp_exe
  
if __name__ == '__main__':
  unit_test.main()
