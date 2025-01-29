#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import socket

from bes.files.bf_check import bf_check
from bes.files.bf_broken_symlink_error import bf_broken_symlink_error
from bes.files.bf_not_dir_error import bf_not_dir_error
from bes.files.bf_not_file_error import bf_not_file_error
from bes.files.bf_permission_error import bf_permission_error

from bes.files.bf_symlink import bf_symlink
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip
from bes.system.filesystem import filesystem
  
class test_bf_check(unit_test):

  def test_check_file_success(self):
    f = self.make_temp_file(content = 'kiwi')
    self.assertEqual( f, bf_check.check_file(f) )

  def test_check_file_allow_none(self):
    self.assertEqual( None, bf_check.check_file(None, allow_none = True) )
    
  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_check_file_failure(self):
    d = self.make_temp_dir()
    with self.assertRaises(bf_not_file_error) as ctx:
      bf_check.check_file(d)
    s = self._make_temp_socket('kiwi.socket')
    with self.assertRaises(bf_not_file_error) as ctx:
      bf_check.check_file(s)

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_check_file_symlink_success(self):
    f = self.make_temp_file(content = 'kiwi')
    l = self.make_temp_file(content = 'link')
    bf_symlink.symlink(f, l)
    self.assertEqual( f, bf_check.check_file(l) )

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_check_file_symlink_broken(self):
    f = self.make_temp_file(content = 'kiwi')
    l = self.make_temp_file(content = 'link')
    bf_symlink.symlink(f, l)
    filesystem.remove(f)
    with self.assertRaises(bf_broken_symlink_error) as ctx:
      bf_check.check_file(l)
    
  def test_check_dir_success(self):
    d = self.make_temp_dir()
    self.assertEqual( d, bf_check.check_dir(d) )

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_check_dir_failure(self):
    f = self.make_temp_file(content = 'kiwi')
    with self.assertRaises(bf_not_dir_error) as ctx:
      bf_check.check_dir(f)
    s = self._make_temp_socket('kiwi.socket')
    with self.assertRaises(bf_not_dir_error) as ctx:
      bf_check.check_dir(s)

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_check_dir_symlink_success(self):
    tmp_dir = self.make_temp_dir()
    d = self.make_temp_dir(dir = tmp_dir)
    l = self.make_temp_file(content = 'link', dir = tmp_dir)
    bf_symlink.symlink(d, l)
    self.assertEqual( d, bf_check.check_dir(l) )
    filesystem.remove(tmp_dir)
      
  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_check_dir_symlink_broken(self):
    d = self.make_temp_dir()
    l = self.make_temp_file(content = 'link')
    bf_symlink.symlink(d, l)
    filesystem.remove(d)
    with self.assertRaises(bf_broken_symlink_error) as ctx:
      bf_check.check_dir(l)
      
  def test_check_file_or_dir_success(self):
    f = self.make_temp_file(content = 'kiwi')
    d = self.make_temp_dir()
    self.assertEqual( f, bf_check.check_file_or_dir(f) )
    self.assertEqual( d, bf_check.check_file_or_dir(d) )

  @unit_test_function_skip.skip_if_not_unix(warning = True)
  def test_check_file_or_dir_failure(self):
    s = self._make_temp_socket('kiwi.socket')
    with self.assertRaises(bf_not_file_error) as ctx:
      bf_check.check_file_or_dir(s)
    
  def _make_temp_socket(self, filename):
    tmp_dir = self.make_temp_dir(dir = path.dirname(__file__))
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
      p = path.join(tmp_dir, filename)
      sock.bind(p)
      return p

  def test_check_file_not_found(self):
    f = self.make_temp_file(non_existent = True)
    d = self.make_temp_file(non_existent = True)
    with self.assertRaises(FileNotFoundError) as ctx:
      bf_check.check_file(f)
    with self.assertRaises(FileNotFoundError) as ctx:
      bf_check.check_dir(d)
    with self.assertRaises(FileNotFoundError) as ctx:
      bf_check.check_file_or_dir(f)
    with self.assertRaises(FileNotFoundError) as ctx:
      bf_check.check_file_or_dir(d)
    
if __name__ == '__main__':
  unit_test.main()
    
