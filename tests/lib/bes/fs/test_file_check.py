#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import socket

from bes.fs.file_check import file_check
from bes.fs.file_symlink import file_symlink
from bes.fs.file_util import file_util
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip
  
class test_file_check(unit_test):

  def test_check_file_success(self):
    f = self.make_temp_file(content = 'kiwi')
    self.assertEqual( f, file_check.check_file(f) )

  def test_check_file_allow_none(self):
    self.assertEqual( None, file_check.check_file(None, allow_none = True) )
    
  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_check_file_failure(self):
    d = self.make_temp_dir()
    with self.assertRaises(IOError) as ctx:
      file_check.check_file(d)
    s = self._make_temp_socket('kiwi.socket')
    with self.assertRaises(IOError) as ctx:
      file_check.check_file(s)

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_check_file_symlink_success(self):
    f = self.make_temp_file(content = 'kiwi')
    l = self.make_temp_file(content = 'link')
    file_symlink.symlink(f, l)
    self.assertEqual( f, file_check.check_file(l) )

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_check_file_symlink_broken(self):
    f = self.make_temp_file(content = 'kiwi')
    l = self.make_temp_file(content = 'link')
    file_symlink.symlink(f, l)
    file_util.remove(f)
    with self.assertRaises(IOError) as ctx:
      file_check.check_file(l)
    
  def test_check_dir_success(self):
    d = self.make_temp_dir()
    self.assertEqual( d, file_check.check_dir(d) )

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_check_dir_failure(self):
    f = self.make_temp_file(content = 'kiwi')
    with self.assertRaises(IOError) as ctx:
      file_check.check_dir(f)
    s = self._make_temp_socket('kiwi.socket')
    with self.assertRaises(IOError) as ctx:
      file_check.check_dir(s)

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_check_dir_symlink_success(self):
    tmp_dir = self.make_temp_dir()
    d = self.make_temp_dir(dir = tmp_dir)
    l = self.make_temp_file(content = 'link', dir = tmp_dir)
    file_symlink.symlink(d, l)
    self.assertEqual( d, file_check.check_dir(l) )
    file_util.remove(tmp_dir)
      
  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_check_dir_symlink_broken(self):
    d = self.make_temp_dir()
    l = self.make_temp_file(content = 'link')
    file_symlink.symlink(d, l)
    file_util.remove(d)
    with self.assertRaises(IOError) as ctx:
      file_check.check_dir(l)
      
  def test_check_file_or_dir_success(self):
    f = self.make_temp_file(content = 'kiwi')
    d = self.make_temp_dir()
    self.assertEqual( f, file_check.check_file_or_dir(f) )
    self.assertEqual( d, file_check.check_file_or_dir(d) )

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_check_file_or_dir_failure(self):
    s = self._make_temp_socket('kiwi.socket')
    with self.assertRaises(IOError) as ctx:
      file_check.check_file_or_dir(s)
    
  def _make_temp_socket(self, filename):
    tmp_dir = self.make_temp_dir(dir = path.dirname(__file__))
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
      p = path.join(tmp_dir, filename)
      sock.bind(p)
      return p
    
if __name__ == '__main__':
  unit_test.main()
    
