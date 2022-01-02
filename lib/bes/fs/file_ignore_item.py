#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple
from bes.common.check import check
from bes.common.object_util import object_util
from bes.text.text_line_parser import text_line_parser

from .file_path import file_path
from .file_util import file_util
from .file_match import file_match

class file_ignore_item(namedtuple('file_ignore_item', 'directory, patterns')):

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
    text = file_util.read(filename, codec = 'utf-8')
    patterns = text_line_parser.parse_lines(text).to_list()
    return file_ignore_item(path.dirname(filename), patterns)
  
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
    ancestors = file_path.decompose(ford)
    for ancestor in ancestors:
      ancestor_dirname = path.dirname(ancestor)
      ancestor_basename = path.basename(ancestor)
      data = self._get_data(ancestor_dirname)
      if data.should_ignore(ancestor_basename):
        return True
    return False
  
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
      return file_ignore_item(d, None)
    return file_ignore_item.read_file(ignore_filename)

  def filter_files(self, files):
    check.check_string_seq(files)
    return [ f for f in files if not self.should_ignore(f) ]

class file_multi_ignore(object):

  def __init__(self, ignore_filenames):
    ignore_filenames = object_util.listify(ignore_filenames)
    self._ignorers = [ file_ignore(f) for f in ignore_filenames ]
    
  def should_ignore(self, ford):
    for ignorer in self._ignorers:
      if ignorer.should_ignore(ford):
        return True
    return False

  def filter_files(self, files):
    check.check_string_seq(files)
    check.check_string_seq(files)
    return [ f for f in files if not self.should_ignore(f) ]
