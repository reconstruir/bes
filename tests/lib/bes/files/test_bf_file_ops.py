#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path
import stat
import time
import unittest

from bes.testing.unit_test import unit_test
from bes.files.bf_file_ops import bf_file_ops

class test_bf_file_ops(unit_test):

  # mkdir

  def test_mkdir(self):
    tmp_dir = self.make_temp_dir()
    new_dir = path.join(tmp_dir, 'new_dir')
    self.assertFalse(path.exists(new_dir))
    bf_file_ops.mkdir(new_dir)
    self.assertTrue(path.isdir(new_dir))

  def test_mkdir_nested(self):
    tmp_dir = self.make_temp_dir()
    new_dir = path.join(tmp_dir, 'a', 'b', 'c')
    bf_file_ops.mkdir(new_dir)
    self.assertTrue(path.isdir(new_dir))

  def test_mkdir_existing_does_not_raise(self):
    tmp_dir = self.make_temp_dir()
    bf_file_ops.mkdir(tmp_dir)
    self.assertTrue(path.isdir(tmp_dir))

  # ensure_file_dir

  def test_ensure_file_dir_creates_parent(self):
    tmp_dir = self.make_temp_dir()
    new_file = path.join(tmp_dir, 'subdir', 'file.txt')
    self.assertFalse(path.exists(path.dirname(new_file)))
    bf_file_ops.ensure_file_dir(new_file)
    self.assertTrue(path.isdir(path.dirname(new_file)))

  def test_ensure_file_dir_existing_parent(self):
    tmp_dir = self.make_temp_dir()
    new_file = path.join(tmp_dir, 'file.txt')
    bf_file_ops.ensure_file_dir(new_file)
    self.assertTrue(path.isdir(tmp_dir))

  def test_ensure_file_dir_nested(self):
    tmp_dir = self.make_temp_dir()
    new_file = path.join(tmp_dir, 'a', 'b', 'c', 'file.txt')
    bf_file_ops.ensure_file_dir(new_file)
    self.assertTrue(path.isdir(path.join(tmp_dir, 'a', 'b', 'c')))

  # remove

  def test_remove_file(self):
    f = self.make_temp_file(content = 'kiwi')
    self.assertTrue(path.exists(f))
    bf_file_ops.remove(f)
    self.assertFalse(path.exists(f))

  def test_remove_non_existent_does_not_raise(self):
    tmp = self.make_temp_file(non_existent = True)
    bf_file_ops.remove(tmp)

  def test_remove_list(self):
    f1 = self.make_temp_file(content = 'kiwi')
    f2 = self.make_temp_file(content = 'orange')
    bf_file_ops.remove([ f1, f2 ])
    self.assertFalse(path.exists(f1))
    self.assertFalse(path.exists(f2))

  def test_remove_list_with_non_existent(self):
    f1 = self.make_temp_file(content = 'kiwi')
    f2 = self.make_temp_file(non_existent = True)
    bf_file_ops.remove([ f1, f2 ])
    self.assertFalse(path.exists(f1))

  # save

  def test_save_non_existent_no_content(self):
    tmp = self.make_temp_file(non_existent = True)
    self.assertFalse(path.exists(tmp))
    bf_file_ops.save(tmp)
    self.assertTrue(path.exists(tmp))

  def test_save_existing_no_content(self):
    tmp = self.make_temp_file(non_existent = False)
    self.assertTrue(path.exists(tmp))
    bf_file_ops.save(tmp)
    self.assertTrue(path.exists(tmp))

  def test_save_non_existent_with_content_string(self):
    tmp = self.make_temp_file(non_existent = True)
    content = 'kiwi'
    bf_file_ops.save(tmp, content = content)
    with open(tmp, 'r') as f:
      self.assertEqual( content, f.read() )

  def test_save_non_existent_with_content_bytes(self):
    tmp = self.make_temp_file(non_existent = True)
    content = b'\x31\x42\x59\x26\x53\x58'
    bf_file_ops.save(tmp, content = content)
    with open(tmp, 'rb') as f:
      self.assertEqual( content, f.read() )

  def test_save_non_existent_with_content_invalid(self):
    tmp = self.make_temp_file(non_existent = True)
    with self.assertRaises(TypeError):
      bf_file_ops.save(tmp, content = 42)

  def test_save_unicode_content_utf8(self):
    tmp = self.make_temp_file(non_existent = True)
    content = 'kiwi ★ Čerova ➨ caf\xe9'
    bf_file_ops.save(tmp, content = content)
    with open(tmp, 'rb') as f:
      self.assertEqual( content, f.read().decode('utf-8') )

  def test_save_default_encoding_is_utf8(self):
    tmp = self.make_temp_file(non_existent = True)
    content = '日本語テスト'
    bf_file_ops.save(tmp, content = content)
    with open(tmp, 'rb') as f:
      self.assertEqual( content, f.read().decode('utf-8') )

  def test_save_explicit_encoding(self):
    tmp = self.make_temp_file(non_existent = True)
    content = 'hello'
    bf_file_ops.save(tmp, content = content, encoding = 'ascii')
    with open(tmp, 'rb') as f:
      self.assertEqual( content.encode('ascii'), f.read() )

  def test_save_bytes_with_encoding_raises(self):
    tmp = self.make_temp_file(non_existent = True)
    with self.assertRaises(ValueError):
      bf_file_ops.save(tmp, content = b'bytes', encoding = 'utf-8')

  def test_save_overwrites_existing(self):
    tmp = self.make_temp_file(content = 'old')
    bf_file_ops.save(tmp, content = 'new')
    with open(tmp, 'rb') as f:
      self.assertEqual( b'new', f.read() )

  def test_save_creates_parent_dirs(self):
    tmp_dir = self.make_temp_dir()
    new_file = path.join(tmp_dir, 'subdir', 'file.txt')
    self.assertFalse(path.exists(path.dirname(new_file)))
    bf_file_ops.save(new_file, content = 'hello')
    self.assertTrue(path.exists(new_file))

  def test_save_returns_filename(self):
    tmp = self.make_temp_file(non_existent = True)
    result = bf_file_ops.save(tmp, content = 'hello')
    self.assertEqual( tmp, result )

  def test_save_writes_lf_not_crlf(self):
    tmp = self.make_temp_file(non_existent = True)
    content = 'line1\nline2\nline3'
    bf_file_ops.save(tmp, content = content)
    with open(tmp, 'rb') as f:
      raw = f.read()
    self.assertNotIn(b'\r\n', raw)
    self.assertIn(b'\n', raw)

  # save_text

  def test_save_text_basic(self):
    tmp = self.make_temp_file(non_existent = True)
    text = 'hello world'
    bf_file_ops.save_text(tmp, text)
    with open(tmp, 'rb') as f:
      self.assertEqual( text.encode('utf-8'), f.read() )

  def test_save_text_unicode(self):
    tmp = self.make_temp_file(non_existent = True)
    text = 'caf\xe9 ★'
    bf_file_ops.save_text(tmp, text)
    with open(tmp, 'rb') as f:
      self.assertEqual( text.encode('utf-8'), f.read() )

  def test_save_text_explicit_encoding(self):
    tmp = self.make_temp_file(non_existent = True)
    text = 'hello'
    bf_file_ops.save_text(tmp, text, encoding = 'ascii')
    with open(tmp, 'rb') as f:
      self.assertEqual( text.encode('ascii'), f.read() )

  def test_save_text_returns_filename(self):
    tmp = self.make_temp_file(non_existent = True)
    result = bf_file_ops.save_text(tmp, 'hello')
    self.assertEqual( tmp, result )

  def test_save_text_creates_parent_dirs(self):
    tmp_dir = self.make_temp_dir()
    new_file = path.join(tmp_dir, 'subdir', 'file.txt')
    bf_file_ops.save_text(new_file, 'hello')
    self.assertTrue(path.exists(new_file))

  # read_text

  def test_read_text_basic(self):
    tmp = self.make_temp_file(non_existent = True)
    bf_file_ops.save(tmp, content = 'hello world')
    self.assertEqual( 'hello world', bf_file_ops.read_text(tmp) )

  def test_read_text_normalizes_crlf(self):
    tmp = self.make_temp_file(non_existent = True)
    with open(tmp, 'wb') as f:
      f.write(b'line1\r\nline2\r\nline3')
    result = bf_file_ops.read_text(tmp)
    self.assertEqual( 'line1\nline2\nline3', result )

  def test_read_text_lf_unchanged(self):
    tmp = self.make_temp_file(non_existent = True)
    with open(tmp, 'wb') as f:
      f.write(b'line1\nline2\nline3')
    self.assertEqual( 'line1\nline2\nline3', bf_file_ops.read_text(tmp) )

  def test_read_text_default_encoding_utf8(self):
    tmp = self.make_temp_file(non_existent = True)
    text = 'caf\xe9 ★'
    with open(tmp, 'wb') as f:
      f.write(text.encode('utf-8'))
    self.assertEqual( text, bf_file_ops.read_text(tmp) )

  def test_read_text_explicit_encoding(self):
    tmp = self.make_temp_file(non_existent = True)
    text = 'caf\xe9'
    with open(tmp, 'wb') as f:
      f.write(text.encode('latin-1'))
    self.assertEqual( text, bf_file_ops.read_text(tmp, encoding = 'latin-1') )

  def test_read_text_non_existent_raises(self):
    tmp = self.make_temp_file(non_existent = True)
    with self.assertRaises(Exception):
      bf_file_ops.read_text(tmp)

  # backup

  def test_backup_non_existent_returns_none(self):
    tmp = self.make_temp_file(non_existent = True)
    result = bf_file_ops.backup(tmp)
    self.assertIsNone(result)

  def test_backup_creates_bak_file(self):
    tmp = self.make_temp_file(content = 'hello')
    backup_path = bf_file_ops.backup(tmp)
    self.assertEqual( tmp + '.bak', backup_path )
    self.assertTrue(path.exists(backup_path))
    self.assertEqual( True, bf_file_ops.files_are_the_same(tmp, backup_path) )

  def test_backup_same_content_returns_none(self):
    tmp = self.make_temp_file(content = 'hello')
    bf_file_ops.copy(tmp, tmp + '.bak')
    result = bf_file_ops.backup(tmp)
    self.assertIsNone(result)

  def test_backup_different_existing_backup_overwrites(self):
    tmp = self.make_temp_file(content = 'new content')
    bf_file_ops.save(tmp + '.bak', content = 'old content')
    backup_path = bf_file_ops.backup(tmp)
    self.assertEqual( tmp + '.bak', backup_path )
    self.assertEqual( True, bf_file_ops.files_are_the_same(tmp, backup_path) )

  def test_backup_custom_suffix(self):
    tmp = self.make_temp_file(content = 'hello')
    backup_path = bf_file_ops.backup(tmp, suffix = '.backup')
    self.assertEqual( tmp + '.backup', backup_path )
    self.assertTrue(path.exists(backup_path))

  def test_backup_not_a_file_raises(self):
    tmp_dir = self.make_temp_dir()
    with self.assertRaises(RuntimeError):
      bf_file_ops.backup(tmp_dir)

  # same_device_id

  def test_same_device_id_same_dir(self):
    tmp_dir = self.make_temp_dir()
    f1 = path.join(tmp_dir, 'a.txt')
    f2 = path.join(tmp_dir, 'b.txt')
    bf_file_ops.save(f1, content = 'a')
    bf_file_ops.save(f2, content = 'b')
    self.assertTrue(bf_file_ops.same_device_id(f1, f2))

  # rename

  def test_rename_basic(self):
    src = self.make_temp_file(content = 'hello')
    tmp_dir = self.make_temp_dir()
    dst = path.join(tmp_dir, 'renamed.txt')
    bf_file_ops.rename(src, dst)
    self.assertFalse(path.exists(src))
    self.assertTrue(path.exists(dst))
    with open(dst, 'rb') as f:
      self.assertEqual( b'hello', f.read() )

  def test_rename_creates_parent_dir(self):
    src = self.make_temp_file(content = 'hello')
    tmp_dir = self.make_temp_dir()
    dst = path.join(tmp_dir, 'subdir', 'renamed.txt')
    bf_file_ops.rename(src, dst)
    self.assertTrue(path.exists(dst))

  # copy

  def test_copy_basic(self):
    src = self.make_temp_file(content = 'hello')
    tmp_dir = self.make_temp_dir()
    dst = path.join(tmp_dir, 'copy.txt')
    bf_file_ops.copy(src, dst)
    self.assertTrue(path.exists(src))
    self.assertTrue(path.exists(dst))
    self.assertEqual( True, bf_file_ops.files_are_the_same(src, dst) )

  def test_copy_src_equals_dst_raises(self):
    src = self.make_temp_file(content = 'hello')
    with self.assertRaises(IOError):
      bf_file_ops.copy(src, src)

  def test_copy_creates_parent_dirs(self):
    src = self.make_temp_file(content = 'hello')
    tmp_dir = self.make_temp_dir()
    dst = path.join(tmp_dir, 'subdir', 'copy.txt')
    bf_file_ops.copy(src, dst)
    self.assertTrue(path.exists(dst))

  def test_copy_overwrites_existing(self):
    src = self.make_temp_file(content = 'new')
    dst = self.make_temp_file(content = 'old')
    bf_file_ops.copy(src, dst)
    self.assertEqual( True, bf_file_ops.files_are_the_same(src, dst) )

  # copy_mode

  @unittest.skipIf(os.name == 'nt', 'chmod not fully supported on Windows')
  def test_copy_mode(self):
    src = self.make_temp_file(content = 'hello')
    dst = self.make_temp_file(content = 'world')
    os.chmod(src, 0o755)
    bf_file_ops.copy_mode(src, dst)
    src_mode = stat.S_IMODE(os.stat(src).st_mode)
    dst_mode = stat.S_IMODE(os.stat(dst).st_mode)
    self.assertEqual( src_mode, dst_mode )

  # read

  def test_read_without_encoding_returns_bytes(self):
    content = b'\x00\x01\x02\x03\xff'
    tmp = self.make_temp_file(non_existent = True)
    with open(tmp, 'wb') as f:
      f.write(content)
    result = bf_file_ops.read(tmp)
    self.assertIsInstance(result, bytes)
    self.assertEqual( content, result )

  def test_read_with_encoding_returns_str(self):
    text = 'hello world'
    tmp = self.make_temp_file(non_existent = True)
    bf_file_ops.save(tmp, content = text)
    result = bf_file_ops.read(tmp, encoding = 'utf-8')
    self.assertIsInstance(result, str)
    self.assertEqual( text, result )

  def test_read_unicode_with_encoding(self):
    text = 'caf\xe9 ★'
    tmp = self.make_temp_file(non_existent = True)
    bf_file_ops.save(tmp, content = text)
    result = bf_file_ops.read(tmp, encoding = 'utf-8')
    self.assertEqual( text, result )

  def test_read_normalizes_crlf_with_encoding(self):
    tmp = self.make_temp_file(non_existent = True)
    with open(tmp, 'wb') as f:
      f.write(b'a\r\nb\r\nc')
    result = bf_file_ops.read(tmp, encoding = 'utf-8')
    self.assertEqual( 'a\nb\nc', result )

  # read_as_lines
  # note: read_as_lines splits on os.sep (the path separator), not newlines

  def test_read_as_lines(self):
    content = os.sep.join([ 'a', 'b', 'c' ])
    tmp = self.make_temp_file(non_existent = True)
    with open(tmp, 'w', encoding = 'utf-8') as f:
      f.write(content)
    result = bf_file_ops.read_as_lines(tmp)
    self.assertEqual( [ 'a', 'b', 'c' ], result )

  def test_read_as_lines_ignore_empty_true(self):
    content = os.sep + 'a' + os.sep + 'b' + os.sep
    tmp = self.make_temp_file(non_existent = True)
    with open(tmp, 'w', encoding = 'utf-8') as f:
      f.write(content)
    result = bf_file_ops.read_as_lines(tmp, ignore_empty = True)
    self.assertEqual( [ 'a', 'b' ], result )

  def test_read_as_lines_ignore_empty_false(self):
    content = os.sep + 'a' + os.sep + 'b'
    tmp = self.make_temp_file(non_existent = True)
    with open(tmp, 'w', encoding = 'utf-8') as f:
      f.write(content)
    result = bf_file_ops.read_as_lines(tmp, ignore_empty = False)
    self.assertEqual( [ '', 'a', 'b' ], result )

  # relocate_file

  def test_relocate_file(self):
    src = self.make_temp_file(content = 'hello')
    src_basename = path.basename(src)
    dst_dir = self.make_temp_dir()
    result = bf_file_ops.relocate_file(src, dst_dir)
    expected_dst = path.join(dst_dir, src_basename)
    self.assertEqual( expected_dst, result )
    self.assertFalse(path.exists(src))
    self.assertTrue(path.exists(result))
    with open(result, 'rb') as f:
      self.assertEqual( b'hello', f.read() )

  # open_with_default

  def test_open_with_default_write_text(self):
    tmp = self.make_temp_file(non_existent = True)
    with bf_file_ops.open_with_default(filename = tmp) as f:
      f.write('hello world')
    with open(tmp, 'rb') as f:
      self.assertEqual( b'hello world', f.read() )

  def test_open_with_default_unicode(self):
    tmp = self.make_temp_file(non_existent = True)
    content = 'caf\xe9 ★ 日本語'
    with bf_file_ops.open_with_default(filename = tmp) as f:
      f.write(content)
    with open(tmp, 'rb') as f:
      self.assertEqual( content, f.read().decode('utf-8') )

  def test_open_with_default_no_crlf_translation(self):
    tmp = self.make_temp_file(non_existent = True)
    with bf_file_ops.open_with_default(filename = tmp) as f:
      f.write('line1\nline2\nline3')
    with open(tmp, 'rb') as f:
      raw = f.read()
    self.assertNotIn(b'\r\n', raw)
    self.assertEqual( b'line1\nline2\nline3', raw )

  def test_open_with_default_binary_mode(self):
    tmp = self.make_temp_file(non_existent = True)
    data = b'\x00\x01\x02\x03\xff'
    with bf_file_ops.open_with_default(filename = tmp, mode = 'wb') as f:
      f.write(data)
    with open(tmp, 'rb') as f:
      self.assertEqual( data, f.read() )

  def test_open_with_default_dash_uses_stdout(self):
    import io
    with bf_file_ops.open_with_default(filename = '-') as f:
      self.assertIsNotNone(f)

  # files_are_the_same

  def test_files_are_the_same_true(self):
    f1 = self.make_temp_file(content = 'abcdefghijklmnopqrstuvwxyz')
    f2 = self.make_temp_file(content = 'abcdefghijklmnopqrstuvwxyz')
    self.assertEqual( True, bf_file_ops.files_are_the_same(f1, f2) )

  def test_files_are_the_same_false(self):
    f1 = self.make_temp_file(content = 'abcdefghijklmnopqrstuvwxyz')
    f2 = self.make_temp_file(content = 'abcdefghijklmnopqrstuvwxy')
    self.assertEqual( False, bf_file_ops.files_are_the_same(f1, f2) )

  def test_files_are_the_same_both_empty(self):
    f1 = self.make_temp_file(content = '')
    f2 = self.make_temp_file(content = '')
    self.assertEqual( True, bf_file_ops.files_are_the_same(f1, f2) )

  def test_files_are_the_same_one_empty(self):
    f1 = self.make_temp_file(content = 'hello')
    f2 = self.make_temp_file(content = '')
    self.assertEqual( False, bf_file_ops.files_are_the_same(f1, f2) )

  def test_files_are_the_same_same_file(self):
    f1 = self.make_temp_file(content = 'hello')
    self.assertEqual( True, bf_file_ops.files_are_the_same(f1, f1) )

  def test_files_are_the_same_binary(self):
    data = bytes(range(256))
    f1 = self.make_temp_file(non_existent = True)
    f2 = self.make_temp_file(non_existent = True)
    with open(f1, 'wb') as f:
      f.write(data)
    with open(f2, 'wb') as f:
      f.write(data)
    self.assertEqual( True, bf_file_ops.files_are_the_same(f1, f2) )

  # touch

  def test_touch_creates_new_file(self):
    tmp = self.make_temp_file(non_existent = True)
    self.assertFalse(path.exists(tmp))
    bf_file_ops.touch(tmp)
    self.assertTrue(path.exists(tmp))

  def test_touch_creates_new_file_empty(self):
    tmp = self.make_temp_file(non_existent = True)
    bf_file_ops.touch(tmp)
    self.assertEqual( 0, os.stat(tmp).st_size )

  def test_touch_existing_file_preserves_content(self):
    tmp = self.make_temp_file(content = 'hello')
    bf_file_ops.touch(tmp)
    with open(tmp, 'rb') as f:
      self.assertEqual( b'hello', f.read() )

  def test_touch_existing_file_updates_mtime(self):
    tmp = self.make_temp_file(content = 'hello')
    past = self.make_temp_file(non_existent = True)
    from datetime import datetime, timezone
    past_dt = datetime(2000, 1, 1, tzinfo = timezone.utc)
    os.utime(tmp, (past_dt.timestamp(), past_dt.timestamp()))
    mtime_before = os.stat(tmp).st_mtime
    bf_file_ops.touch(tmp)
    mtime_after = os.stat(tmp).st_mtime
    self.assertGreater(mtime_after, mtime_before)

  def test_touch_creates_parent_dirs(self):
    tmp_dir = self.make_temp_dir()
    new_file = path.join(tmp_dir, 'subdir', 'file.txt')
    bf_file_ops.touch(new_file)
    self.assertTrue(path.exists(new_file))

  # hard_link

  @unittest.skipIf(os.name == 'nt', 'hard links may require elevated privileges on Windows')
  def test_hard_link_basic(self):
    src = self.make_temp_file(content = 'hello')
    tmp_dir = self.make_temp_dir()
    dst = path.join(tmp_dir, 'link.txt')
    bf_file_ops.hard_link(src, dst)
    self.assertTrue(path.exists(dst))
    with open(dst, 'rb') as f:
      self.assertEqual( b'hello', f.read() )

  @unittest.skipIf(os.name == 'nt', 'hard links may require elevated privileges on Windows')
  def test_hard_link_dst_is_dir_raises(self):
    src = self.make_temp_file(content = 'hello')
    dst_dir = self.make_temp_dir()
    with self.assertRaises(IOError):
      bf_file_ops.hard_link(src, dst_dir)

  @unittest.skipIf(os.name == 'nt', 'hard links may require elevated privileges on Windows')
  def test_hard_link_replaces_existing_dst(self):
    src = self.make_temp_file(content = 'new')
    dst = self.make_temp_file(content = 'old')
    bf_file_ops.hard_link(src, dst)
    with open(dst, 'rb') as f:
      self.assertEqual( b'new', f.read() )

if __name__ == '__main__':
  unit_test.main()
