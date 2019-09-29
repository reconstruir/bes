#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, shutil, tempfile
from bes.testing.unit_test import unit_test
from bes.fs.testing.temp_content import temp_content as I
from bes.testing.unit_test_skip import skip_if_not_unix

class test_temp_content(unit_test):

  def test_parse_string(self):
    self.assertEqual( I( I.FILE, 'foo.txt', 'this is foo\nhaha', None ), I.parse('file foo.txt "this is foo\nhaha"') )
    self.assertEqual( ( I.FILE, 'foo.txt', None, None ), I.parse('file foo.txt') )
    self.assertEqual( ( I.DIR, 'foo', None, None ), I.parse('dir foo') )
    self.assertEqual( ( I.FILE, 'foo.txt', None, 0o755 ), I.parse('file foo.txt "" 755') )

  def test_parse_tuple(self):
    self.assertEqual( ( I.FILE, 'foo.txt', None, None ), I.parse( ('file', 'foo.txt' ) ) )
    self.assertEqual( ( I.FILE, 'foo.txt', 'this is foo\nhaha', None ), I.parse( ('file', 'foo.txt', 'this is foo\nhaha') ) )

  def test_write(self):
    i = I(I.FILE, 'foo.txt', 'this is foo\nhaha', 0o644)
    tmp_dir = tempfile.mkdtemp()
    i.write(tmp_dir)
    p = path.join(tmp_dir, 'foo.txt')
    self.assertTrue( path.exists(p) )
    with open(p, 'r') as fin:
      self.assertEqual( 'this is foo\nhaha', fin.read() )
    shutil.rmtree(tmp_dir)

  def test_write_with_filename(self):
    tmp_file = self.make_temp_file(content = 'this is foo\nhaha')
    i = I(I.FILE, 'foo.txt', 'file:{}'.format(tmp_file), 0o644)
    tmp_dir = tempfile.mkdtemp()
    i.write(tmp_dir)
    p = path.join(tmp_dir, 'foo.txt')
    self.assertTrue( path.exists(p) )
    with open(p, 'r') as fin:
      self.assertEqual( 'this is foo\nhaha', fin.read() )
    shutil.rmtree(tmp_dir)
    
  @skip_if_not_unix
  def test_write_mode(self):
    i = I(I.FILE, 'foo.txt', 'this is foo\nhaha', 0o644)
    tmp_dir = tempfile.mkdtemp()
    i.write(tmp_dir)
    p = path.join(tmp_dir, 'foo.txt')
    self.assertTrue( path.exists(p) )
    self.assertEqual( 0o644, os.stat(p).st_mode & 0o777 )
    
  def test_write_dir(self):
    tmp_dir = tempfile.mkdtemp()
    I.parse('d mydir').write(tmp_dir)
    self.assertTrue( path.isdir(path.join(tmp_dir, 'mydir')) )
    shutil.rmtree(tmp_dir)

  def test_parse_sequence(self):
    expected = (
      ( 'file', 'foo.txt', 'foo content', 0o755 ),
      ( 'file', 'bar.txt', 'bar content', 0o644 ),
      ( 'dir', 'baz', None, 0o700 ),
    )
    self.assertEqual( expected, I.parse_sequence([
      'file foo.txt "foo content" 755',
      'file bar.txt "bar content" 644',
      'dir  baz     ""            700',
    ]) )

  def test_write_items(self):
    tmp_dir = tempfile.mkdtemp()
    I.write_items([
      'file a/b/c/foo.txt "foo content" 755',
      'file d/e/bar.txt "bar content" 644',
      'dir  baz     ""            700',
    ], tmp_dir)
    self.assertTrue( path.isfile(path.join(tmp_dir, self.p('a/b/c/foo.txt'))) )
    self.assertTrue( path.isfile(path.join(tmp_dir, self.p('d/e/bar.txt'))) )
    self.assertTrue( path.isdir(path.join(tmp_dir, self.p('baz'))) )
    shutil.rmtree(tmp_dir)

  def test_write_items_with_parse(self):
    items = I.parse_sequence([
      'file a/b/c/foo.txt "foo content" 755',
      'file d/e/bar.txt "bar content" 644',
      'dir  baz     ""            700',
    ])
    tmp_dir = tempfile.mkdtemp()
    I.write_items(items, tmp_dir)
    self.assertTrue( path.isfile(path.join(tmp_dir, self.p('a/b/c/foo.txt'))) )
    self.assertTrue( path.isfile(path.join(tmp_dir, self.p('d/e/bar.txt'))) )
    self.assertTrue( path.isdir(path.join(tmp_dir, self.p('baz'))) )
    shutil.rmtree(tmp_dir)

if __name__ == "__main__":
  unit_test.main()
