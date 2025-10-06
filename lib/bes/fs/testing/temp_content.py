#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os, os.path as path
from datetime import datetime

from bes.text.string_list_parser import string_list_parser
from bes.common.string_util import string_util
from bes.system.check import check
from bes.fs.temp_file import temp_file
from bes.files.bf_path import bf_path

class multiplied_temp_content(namedtuple('multiplied_temp_content', 'name, num, size')):
    
  def __new__(clazz, name, num, size = None):
    return clazz.__bases__[0].__new__(clazz, name, num, size)

class temp_content(namedtuple('temp_content', 'item_type, filename, content, mode')):
  'Temporary files, directories and content for easier testing.'
  
  FILE = 'file'
  DIR = 'dir'
  LINK = 'link'
  RESOURCE_FORK = 'resource_fork'

  def __new__(clazz, item_type, filename, content = None, mode = None):
    item_type = clazz.validate_item_type(item_type)
    if mode is not None:
      mode = clazz.validate_mode(mode)
    return clazz.__bases__[0].__new__(clazz, item_type, filename, content, mode)
  
  @classmethod
  def parse_item_type(clazz, s):
    if isinstance(s, temp_content):
      return s
    elif string_util.is_string(s):
      s = s.lower()
      if s in [ 'file', 'f' ]:
        return clazz.FILE
      elif s in [ 'dir', 'd' ]:
        return clazz.DIR
      elif s in [ 'link', 'l' ]:
        return clazz.LINK
      elif s in [ 'resource_fork', 'rf' ]:
        return clazz.RESOURCE_FORK
    return None
    
  @classmethod
  def parse_mode(clazz, m):
    if string_util.is_string(m):
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
    if string_util.is_string(item):
      return clazz._parse_string(item)
    elif isinstance(item, list):
      return clazz._parse_tuple(tuple(item))
    elif isinstance(item, tuple):
      return clazz._parse_tuple(item)
    else:
      raise TypeError('not a valid temp item: %s - %s' % (str(item), type(item)))

  @classmethod
  def _parse_string(clazz, s):
    assert string_util.is_string(s)
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
      raise ValueError('no filename given: {}'.format(str(t)))
    filename = bf_path.normalize_sep(filename)
    if len(t) > 2:
      content = t[2] or None
    else:
      content = None
    if len(t) > 3:
      mode = clazz.parse_mode(t[3])
    else:
      mode = None
    return clazz(item_type, filename, content = content, mode = mode)

  @classmethod
  def _file_read(clazz, filename):
    with open(filename, 'rb') as fin:
      return fin.read()

  @classmethod
  def _file_write(clazz, filename, content):
    content = content or b''
    if not isinstance(content, bytes):
      content = content.encode('utf-8')
    clazz._mkdir(path.dirname(filename))
    with open(filename, 'wb') as fout:
      fout.write(content)
      
  def _write_dir(self, root_dir):
    p = path.join(root_dir, self.filename)
    self._mkdir(p, mode = self.mode)

  def _write_file(self, root_dir):
    content = self._determine_content()
    p = path.join(root_dir, self.filename)
    self._file_write(p, content)
    if self.mode:
      os.chmod(p, self.mode)

  def _write_resource_fork(self, root_dir):
    p = path.join(root_dir, self.filename)
    self.write_resource_fork(p)
    if self.mode:
      os.chmod(p, self.mode)

  @classmethod
  def write_resource_fork(clazz, filename):
    apple_resource_fork_with_entry = (
      b"\x00\x05\x16\x07"          # Magic
      b"\x00\x02\x00\x00"          # Version
      b"Mac OS X\x00\x00\x00\x00\x00\x00\x00\x00"  # Filler (16 bytes)
      b"\x00\x01"                  # Number of entries = 1
      b"\x00\x02"                  # Entry ID = Resource fork
      b"\x00\x00\x00\x1C"          # Offset (28 bytes from start)
      b"\x00\x00\x00\x00"          # Length = 0
    )
    with open(filename, 'wb') as fout:
      fout.write(apple_resource_fork_with_entry)    
      
  def _write_link(self, root_dir):
    content = self._determine_content()
    p = path.join(root_dir, self.filename)
    os.symlink(content, p)
    if self.mode:
      os.chmod(p, self.mode)
      
  def _determine_content(self):
    if not self.content:
      return b''
    if check.is_string(self.content) and self.content.startswith('file:'):
      _, _, source_filename = self.content.partition(':')
      source_filename = source_filename.strip()
      if not path.isfile(source_filename):
        raise IOError('source file not found: {}'.format(source_filename))
      return self._file_read(source_filename)
    else:
      return self.content
      
  def write(self, root_dir):
    if self.item_type == self.DIR:
      self._write_dir(root_dir)
    elif self.item_type == self.FILE:
      self._write_file(root_dir)
    elif self.item_type == self.RESOURCE_FORK:
      self._write_resource_fork(root_dir)
    elif self.item_type == self.LINK:
      self._write_link(root_dir)
    else:
      assert False
      
  @classmethod
  def _mkdir(clazz, p, mode = None):
    if path.isdir(p):
      return
    os.makedirs(p)
    if mode:
      os.chmod(p, mode)
      
  @classmethod
  def parse_sequence(clazz, seq):
    l =  [ i for i in seq ]
    return tuple([ clazz.parse(i) for i in l ])

  @classmethod
  def write_items(clazz, items, root_dir):
    'Write temp content items to root_dir can be a sequence of strings to parse or temp_item objects.'
    for item in items:
      item = clazz.parse(item)
      item.write(root_dir)

  @classmethod
  def write_items_to_temp_dir(clazz, items, delete = True, **kargs):
    'Write temp content items to a temporary dir.'
    root_dir = temp_file.make_temp_dir(delete = delete, **kargs)
    clazz.write_items(items, root_dir)
    return root_dir

  @classmethod
  def write_multiplied_items_to_temp_dir(clazz,
                                         multiplied_content_items = None,
                                         content_multiplier = 1,
                                         extra_content_items = None):
    multiplied_content_items = multiplied_content_items or []
    extra_content_items = extra_content_items or []
    multiplied_content_items = [ multiplied_temp_content(c.name, c.num * content_multiplier, size = c.size) for c in multiplied_content_items ]
    content_items = []
    for next_desc in multiplied_content_items:
      for i in range(1, next_desc.num + 1):
        filename = '{}{}.txt'.format(next_desc.name, i)
        text = 'this is {}'.format(filename)
        if next_desc.size != None:
          assert(next_desc.size > len(text))
          num_needed = next_desc.size - len(text)
          text += (num_needed * 'x')
          assert len(text) == next_desc.size
        desc = 'file src/{} "{}" 644'.format(filename, text)
        content_items.append(desc)
    content_items.extend(extra_content_items)
    tmp_dir = clazz.write_items_to_temp_dir(content_items)
    return tmp_dir
