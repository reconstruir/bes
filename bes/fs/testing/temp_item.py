#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import file_util
from bes.text import string_list_parser
from collections import namedtuple

class temp_item(namedtuple('temp_item', 'item_type,filename,content,mode')):

  FILE = 'file'
  DIR = 'dir'

  def __new__(clazz, item_type, filename, content = None, mode = None):
    item_type = clazz.validate_item_type(item_type)
    if mode is not None:
      mode = clazz.validate_mode(mode)
    return clazz.__bases__[0].__new__(clazz, item_type, filename, content, mode)
  
  @classmethod
  def parse_item_type(clazz, s):
    if not isinstance(s, basestring):
      return None
    s = s.lower()
    if s in [ 'file', 'f' ]:
      return clazz.FILE
    elif s in [ 'dir', 'd' ]:
      return clazz.DIR
    return None
    
  @classmethod
  def parse_mode(clazz, m):
    if isinstance(m, basestring):
      return int(m, 8)
    if isinstance(m, int):
      return m
    return None
    
  @classmethod
  def validate_item_type(clazz, s):
    item_type = clazz.parse_item_type(s)
    if not item_type:
      raise TypeError('not a valid item type: %s - %s' % (str(s), type(s)))
    return item_type
    
  @classmethod
  def validate_mode(clazz, s):
    mode = clazz.parse_mode(s)
    if not mode:
      raise TypeError('not a valid mode: %s - %s' % (str(s), type(s)))
    return mode
    
  @classmethod
  def parse(clazz, item):
    if isinstance(item, basestring):
      return clazz._parse_string(item)
    elif isinstance(item, list):
      return clazz._parse_tuple(tuple(item))
    elif isinstance(item, tuple):
      return clazz._parse_tuple(item)
    else:
      raise TypeError('not a valid temp item: %s - %s' % (str(item), type(item)))

  @classmethod
  def _parse_string(clazz, s):
    assert isinstance(s, basestring)
    parts = string_list_parser.parse_to_list(s)
    return clazz._parse_tuple(tuple(parts))

  @classmethod
  def _parse_tuple(clazz, t):
    assert isinstance(t, tuple)
    if len(t) < 2:
      raise ValueError('not a valid item: %s' % (s))
    item_type = clazz.parse_item_type(t[0])
    filename = t[1]
    if not filename:
      raise ValueError('not a valid filename: "%s"' % (filename))
    if len(t) > 2:
      content = t[2] or None
    else:
      content = None
    if content and path.isfile(content):
      content = file_util.read(content)
    if len(t) > 3:
      mode = clazz.parse_mode(t[3])
    else:
      mode = None
    return clazz(item_type, filename, content = content, mode = mode)

  def write(self, root_dir):
    p = path.join(root_dir, self.filename)
    if self.item_type == self.DIR:
      file_util.mkdir(p, mode = self.mode)
    elif self.item_type == self.FILE:
      file_util.save(p, content = self.content, mode = self.mode)
    else:
      assert False

  @classmethod
  def parse_sequence(clazz, seq):
    l =  [ i for i in seq ]
    return tuple([ clazz.parse(i) for i in l ])
      
  '''
  @classmethod
  def _make_temp_items(clazz, items):
    return [ clazz._parse_item(item) for item in items ]

  @classmethod
  def _write_temp_content(clazz, root_dir, items):
    items = clazz._make_temp_items(items)
    for item in items:
      filename = path.join(root_dir, item.filename)
      if item.isdir:
        file_util.mkdir(filename)
      else:
        file_util.save(filename, item.content)

  @classmethod
  def _make_temp_content(clazz, items):
    tmp_dir = temp_file.make_temp_dir()
    clazz._write_temp_content(tmp_dir, items)
    return tmp_dir

  def test_file_find(self):
    tmp_dir = self._make_temp_content([
      ( 'foo.txt', 'foo.txt\n' ),
      ( 'subdir/bar.txt', 'bar.txt\n' ),
      ( 'subdir/subberdir/baz.txt', 'baz.txt\n' ),
      ( 'emptyfile.txt' ),
      ( 'emptydir/' ),
    ])

    expected_relative = [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ]

    self.assertEqual( expected_relative, file_find.find(tmp_dir, relative = True) )

  def test_file_find_absolute(self):
    tmp_dir = self._make_temp_content([
      ( 'foo.txt', 'foo.txt\n' ),
      ( 'subdir/bar.txt', 'bar.txt\n' ),
      ( 'subdir/subberdir/baz.txt', 'baz.txt\n' ),
      ( 'emptyfile.txt' ),
      ( 'emptydir/' ),
    ])

    expected_relative = [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ]
    expected_absolute = [ path.join(tmp_dir, f) for f in expected_relative ]

    self.assertEqual( expected_absolute, file_find.find(tmp_dir, relative = False) )

  def test_file_find_max_depth(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_content([
      ( '1a.f' ),
      ( '1b.f' ),
      ( '1.d/2a.f' ),
      ( '1.d/2b.f' ),
      ( '1.d/2.d/3a.f' ),
      ( '1.d/2.d/3b.f' ),
      ( '1.d/2.d/3.d/4a.f' ),
      ( '1.d/2.d/3.d/4b.f' ),
      ( '1.d/2.d/3.d/4.d/5a.f' ),
      ( '1.d/2.d/3.d/4.d/5b.f' ),
    ])

#    self.assertEqual( sorted([ '1a.f', '1b.f' ]), file_find.find(tmp_dir, max_depth = 0) )
    self.assertEqual( sorted([ '1a.f', '1b.f' ]), file_find.find(tmp_dir, max_depth = 1) )
    self.assertEqual( sorted([ '1a.f', '1b.f', '1.d/2a.f', '1.d/2b.f' ]), file_find.find(tmp_dir, max_depth = 2) )
    self.assertEqual( sorted([ '1a.f', '1b.f', '1.d/2a.f', '1.d/2b.f', '1.d/2.d/3a.f', '1.d/2.d/3b.f' ]), file_find.find(tmp_dir, max_depth = 3) )
    self.assertEqual( sorted([ '1a.f', '1b.f', '1.d/2a.f', '1.d/2b.f', '1.d/2.d/3a.f', '1.d/2.d/3b.f', '1.d/2.d/3.d/4a.f', '1.d/2.d/3.d/4b.f' ]), file_find.find(tmp_dir, max_depth = 4) )
    self.assertEqual( sorted([ '1a.f', '1b.f', '1.d/2a.f', '1.d/2b.f', '1.d/2.d/3a.f', '1.d/2.d/3b.f', '1.d/2.d/3.d/4a.f', '1.d/2.d/3.d/4b.f', '1.d/2.d/3.d/4.d/5a.f', '1.d/2.d/3.d/4.d/5b.f' ]), file_find.find(tmp_dir, max_depth = 5) )

  def test_file_find_min_depth(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_content([
      ( '1a.f' ),
      ( '1b.f' ),
      ( '1.d/2a.f' ),
      ( '1.d/2b.f' ),
      ( '1.d/2.d/3a.f' ),
      ( '1.d/2.d/3b.f' ),
      ( '1.d/2.d/3.d/4a.f' ),
      ( '1.d/2.d/3.d/4b.f' ),
      ( '1.d/2.d/3.d/4.d/5a.f' ),
      ( '1.d/2.d/3.d/4.d/5b.f' ),
    ])

    self.assertEqual( sorted([ '1a.f', '1b.f', '1.d/2a.f', '1.d/2b.f', '1.d/2.d/3a.f', '1.d/2.d/3b.f', '1.d/2.d/3.d/4a.f', '1.d/2.d/3.d/4b.f', '1.d/2.d/3.d/4.d/5a.f', '1.d/2.d/3.d/4.d/5b.f' ]), file_find.find(tmp_dir, min_depth = 1) )
    self.assertEqual( sorted([ '1.d/2a.f', '1.d/2b.f', '1.d/2.d/3a.f', '1.d/2.d/3b.f', '1.d/2.d/3.d/4a.f', '1.d/2.d/3.d/4b.f', '1.d/2.d/3.d/4.d/5a.f', '1.d/2.d/3.d/4.d/5b.f' ]), file_find.find(tmp_dir, min_depth = 2) )
    self.assertEqual( sorted([ '1.d/2.d/3a.f', '1.d/2.d/3b.f', '1.d/2.d/3.d/4a.f', '1.d/2.d/3.d/4b.f', '1.d/2.d/3.d/4.d/5a.f', '1.d/2.d/3.d/4.d/5b.f' ]), file_find.find(tmp_dir, min_depth = 3) )
    self.assertEqual( sorted([ '1.d/2.d/3.d/4a.f', '1.d/2.d/3.d/4b.f', '1.d/2.d/3.d/4.d/5a.f', '1.d/2.d/3.d/4.d/5b.f' ]), file_find.find(tmp_dir, min_depth = 4) )
    self.assertEqual( sorted([ '1.d/2.d/3.d/4.d/5a.f', '1.d/2.d/3.d/4.d/5b.f' ]), file_find.find(tmp_dir, min_depth = 5) )
    self.assertEqual( sorted([]), file_find.find(tmp_dir, min_depth = 6) )

  def test_file_find_min_and_max_depth(self):
    self.maxDiff = None
    tmp_dir = self._make_temp_content([
      ( '1a.f' ),
      ( '1b.f' ),
      ( '1.d/2a.f' ),
      ( '1.d/2b.f' ),
      ( '1.d/2.d/3a.f' ),
      ( '1.d/2.d/3b.f' ),
      ( '1.d/2.d/3.d/4a.f' ),
      ( '1.d/2.d/3.d/4b.f' ),
      ( '1.d/2.d/3.d/4.d/5a.f' ),
      ( '1.d/2.d/3.d/4.d/5b.f' ),
    ])

    self.assertEqual( sorted([ '1a.f', '1b.f', '1.d/2a.f', '1.d/2b.f' ]), file_find.find(tmp_dir, min_depth = 1, max_depth = 2) )
    self.assertEqual( sorted([ '1.d/2a.f', '1.d/2b.f', '1.d/2.d/3a.f', '1.d/2.d/3b.f' ]), file_find.find(tmp_dir, min_depth = 2, max_depth = 3) )
    self.assertEqual( sorted([ '1.d/2a.f', '1.d/2b.f' ]), file_find.find(tmp_dir, min_depth = 2, max_depth = 2) )
    self.assertEqual( sorted([ '1a.f', '1b.f' ]), file_find.find(tmp_dir, min_depth = 1, max_depth = 1) )
'''
  
if __name__ == "__main__":
  unittest.main()
