#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple
from bes.common import check
from bes.text import lines

from .file_path import file_path
from .file_util import file_util

class ignore_file_data(namedtuple('ignore_file_data', 'directory,patterns')):

  def __new__(clazz, directory, patterns):
#    directory = path.abspath(directory)
    check.check_string(directory)
    check.check_string_seq(patterns)
    return clazz.__bases__[0].__new__(clazz, directory, patterns)

  @classmethod
  def read_file(clazz, filename):
    filename = path.abspath(filename)
    if not path.isfile(filename):
      raise IOError('not a file: %s' % (filename))
    text = file_util.read(filename)
    patterns = lines.parse_lines(text)
    return clazz(path.dirname(filename), patterns)
  
class file_ignore(object):
  'Decide whether to ignore a file based on scheme similar to .gitignore'
  
  def __init__(self, ignore_filename):
    self._ignore_filename = ignore_filename

  def ignore(self, filename):
    if not path.isfile(filename):
      raise IOError('not a file: %s' % (filename))
    parents = self._parents(filename)
    print('parents: %s' % (parents))
      
  def _parents(self, filename):
    result = []
    parent = file_path.parent_dir(filename)
    while True:
      result.append(parent)
      parent = file_path.parent_dir(parent)
      if not parent:
        break
    return result
    
