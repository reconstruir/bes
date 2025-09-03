#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check

from bes.files.bf_path import bf_path
from .file_ignore_item import file_ignore_item
  
class file_ignore(object):
  'Decide whether to ignore a file based on scheme similar to .gitignore'
  
  def __init__(self, ignore_filename):
    self._ignore_filename = ignore_filename
    self._data = {}
    
  def should_ignore(self, ford):
    if not path.exists(ford):
      print(f'ERROR: ignoring missing file {ford}')
      return True #raise IOError('not a file or directory: %s' % (ford))
    if not self._ignore_filename:
      return False
    ancestors = bf_path.decompose(ford)
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
