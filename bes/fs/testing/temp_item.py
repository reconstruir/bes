#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, tempfile
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
      with open(content, 'r') as fin:
        content = fin.read()
    if len(t) > 3:
      mode = clazz.parse_mode(t[3])
    else:
      mode = None
    return clazz(item_type, filename, content = content, mode = mode)

  def write(self, root_dir):
    p = path.join(root_dir, self.filename)
    if self.item_type == self.DIR:
      clazz.mkdir(p, mode = self.mode)
    elif self.item_type == self.FILE:
      with open(p, 'w') as fout:
        fout.write(self.content or '')
      if self.mode:
        os.chmod(p, self.mode)
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
