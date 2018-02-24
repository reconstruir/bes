#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple
from bes.common import check
from bes.text import lines

from .file_path import file_path
from .file_util import file_util
from .file_match import file_match

class ignore_file_data(namedtuple('ignore_file_data', 'directory,patterns')):

  def __new__(clazz, directory, patterns):
    check.check_string(directory)
    if patterns:
      check.check_string_seq(patterns)
    return clazz.__bases__[0].__new__(clazz, directory, patterns)

  @classmethod
  def read_file(clazz, filename):
    filename = path.abspath(filename)
    if not path.isfile(filename):
      raise IOError('not a file: %s' % (filename))
    text = file_util.read(filename)
    patterns = lines.parse_lines(text).to_list()
    return clazz(path.dirname(filename), patterns)
  
  def should_ignore(self, filename):
    if not self.patterns:
      return False
    filename = path.basename(filename)
    return file_match.match_fnmatch(filename, self.patterns, file_match.ANY)
  
class file_ignore(object):
  'Decide whether to ignore a file based on scheme similar to .gitignore'
  
  def __init__(self, ignore_filename):
    self._ignore_filename = ignore_filename
    self._data = {}
    
  def should_ignore(self, ford):
    if not path.exists(ford):
      raise IOError('not a file or directory: %s' % (ford))
    if not self._ignore_filename:
      return False
    parents = self._decompose_parents(ford)
    for parent_dir, parent_base in parents:
      data = self._get_data(parent_dir)
      if data.should_ignore(parent_base):
        return True
    return False
  
  def _decompose_parents(self, filename):
    'Return a revered list of tuples of parent basenames and dirnames.'
    assert path.isfile(filename)
    assert path.isabs(filename)
    result = []
    f = path.basename(filename)
    d = path.dirname(filename)
    while True:
      if d == '/':
        break
      result.append( ( d, f ) )
      f = path.basename(d)
      d = path.dirname(d)
    return [ x for x in reversed(result) ]

  def _get_data(self, d):
    if not path.isdir(d):
      raise IOError('not a directory: %s' % (d))
    d = path.abspath(d)
    if d not in self._data:
      self._data[d] = self._load_data(d)
    return self._data[d]
    
  def _load_data(self, d):
    assert path.isdir(d)
    assert path.isabs(d)
    ignore_filename = path.join(d, self._ignore_filename)
    if not path.isfile(ignore_filename):
      return ignore_file_data(d, None)
    return ignore_file_data.read_file(ignore_filename)
