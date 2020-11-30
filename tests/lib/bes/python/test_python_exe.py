#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.testing.unit_test import unit_test
from bes.fs.file_util import file_util
from bes.system.env_override import env_override

from bes.python.python_exe import python_exe
from bes.python.python_error import python_error

class test_python_exe(unit_test):

  def test_full_version(self):
    content = '''\
#!/bin/bash
echo Python 2.7.666 1>&2
exit 0
'''
    fake_exe = self.make_temp_file(content = content, perm = 0o0755)
    self.assertEqual( '2.7.666', python_exe.full_version(fake_exe) )

  def test_version(self):
    content = '''\
#!/bin/bash
echo Python 2.7.666 1>&2
exit 0
'''
    fake_exe = self.make_temp_file(content = content, perm = 0o0755)
    self.assertEqual( '2.7', python_exe.version(fake_exe) )

  def test_find_python_version(self):
    tmp_dir = self.make_temp_dir()

    content = '''\
#!/bin/bash
echo Python 6.7.666 1>&2
exit 0
'''
    fake_exe = file_util.save(path.join(tmp_dir, 'python6.7'), content = content, mode = 0o0755)

    with env_override(env = { 'PATH': tmp_dir }) as env:
      self.assertEqual( fake_exe, python_exe.find_python_version('6.7') )

  def test_find_python_full_version(self):
    tmp_dir = self.make_temp_dir()

    content = '''\
#!/bin/bash
echo Python 6.7.666 1>&2
exit 0
'''
    fake_exe = file_util.save(path.join(tmp_dir, 'python6.7'), content = content, mode = 0o0755)

    with env_override(env = { 'PATH': tmp_dir }) as env:
      self.assertEqual( fake_exe, python_exe.find_python_full_version('6.7.666') )

  def test_has_python_version(self):
    tmp_dir = self.make_temp_dir()

    content = '''\
#!/bin/bash
echo Python 6.7.666 1>&2
exit 0
'''
    fake_exe = file_util.save(path.join(tmp_dir, 'python6.7'), content = content, mode = 0o0755)

    with env_override(env = { 'PATH': tmp_dir }) as env:
      self.assertTrue( python_exe.has_python_version('6.7') )
      self.assertFalse( python_exe.has_python_version('9.8') )
      
  def test_has_python_full_version(self):
    tmp_dir = self.make_temp_dir()

    content = '''\
#!/bin/bash
echo Python 6.7.666 1>&2
exit 0
'''
    fake_exe = file_util.save(path.join(tmp_dir, 'python6.7'), content = content, mode = 0o0755)

    with env_override(env = { 'PATH': tmp_dir }) as env:
      self.assertTrue( python_exe.has_python_full_version('6.7.666') )
      self.assertFalse( python_exe.has_python_full_version('6.7.667') )

  def test_check_exe_success(self):
    tmp_dir = self.make_temp_dir()

    content = '''\
#!/bin/bash
echo Python 6.7.666 1>&2
exit 0
'''
    fake_exe = file_util.save(path.join(tmp_dir, 'python6.7'), content = content, mode = 0o0755)

    self.assertEqual( '6.7.666', python_exe.check_exe(fake_exe) )

  def test_check_exe_not_executable(self):
    tmp_dir = self.make_temp_dir()

    content = '''\
#!/bin/bash
echo Python 6.7.666 1>&2
exit 0
'''
    fake_exe = file_util.save(path.join(tmp_dir, 'python6.7'), content = content, mode = 0o0600)

    with self.assertRaises(python_error) as ctx:
      python_exe.check_exe(fake_exe)
    self.assertTrue( 'not a valid executable' in str(ctx.exception) )
    
  def test_check_exe_not_abs(self):
    tmp_dir = self.make_temp_dir()

    content = '''\
#!/bin/bash
echo Python 6.7.666 1>&2
exit 0
'''
    with self.assertRaises(python_error) as ctx:
      python_exe.check_exe('python6.7')
    self.assertTrue( 'not an absolute path' in str(ctx.exception) )
    
  def test_check_exe_invalid_version(self):
    tmp_dir = self.make_temp_dir()

    content = '''\
#!/bin/bash
echo awk 6.6.6 1>&2
exit 0
'''
    fake_exe = file_util.save(path.join(tmp_dir, 'python6.7'), content = content, mode = 0o0755)

    with self.assertRaises(python_error) as ctx:
      python_exe.check_exe(fake_exe)
    self.assertTrue( 'not a valid python version' in str(ctx.exception) )
    
if __name__ == '__main__':
  unit_test.main()
