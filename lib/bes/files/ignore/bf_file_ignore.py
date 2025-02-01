#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.check import check

from ..bf_path import bf_path
from ..bf_entry import bf_entry
from ..bf_entry_list import bf_entry_list

from .bf_file_ignore_item import bf_file_ignore_item
  
class bf_file_ignore(object):
  'Decide whether to ignore a bf_entry based on scheme similar to .gitignore'
  
  def __init__(self, ignore_filename):
    self._ignore_filename = ignore_filename
    self._data = {}
    
  def should_ignore(self, entry, ignore_missing_files = True):
    check.check_bf_entry(entry)
    check.check_bool(ignore_missing_files)
    
    if not entry.exists:
      if not ignore_missing_files:
        raise FileNotFoundError(f'File not found: {entry.absolute_filename}')
      return True
    if not self._ignore_filename:
      return False
    for ancestor in entry.decomposed_path:
      ancestor_dirname = path.dirname(ancestor)
      ancestor_basename = path.basename(ancestor)
      data = self._get_data(ancestor_dirname)
      if data.should_ignore(bf_entry(ancestor_basename)):
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
      return bf_file_ignore_item(d, None)
    return bf_file_ignore_item.read_file(ignore_filename)

  def filter_entries(self, entries):
    check.check_bf_entry_list(entries)
    return [ entry for entry in entries if not self.should_ignore(entry) ]
