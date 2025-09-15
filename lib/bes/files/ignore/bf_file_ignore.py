#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.check import check
from bes.system.log import logger

from ..bf_path import bf_path
from ..bf_entry import bf_entry
from ..bf_entry_list import bf_entry_list

from .bf_file_ignore_item import bf_file_ignore_item
  
class bf_file_ignore(object):
  'Decide whether to ignore a bf_entry based on scheme similar to .gitignore'

  _log = logger('bf_file_ignore')
  
  def __init__(self, ignore_filename):
    if ignore_filename and ignore_filename != path.basename(ignore_filename):
      raise ValueError(f'ignore_filename should be a basename: "{ignore_filename}"')
    self._ignore_filename = ignore_filename
    self._items = {}

  def should_ignore(self, entry, root_dir, ignore_missing_files = True):
    check.check_bf_entry(entry)
    check.check_string(root_dir)
    check.check_bool(ignore_missing_files)

    try:
      return self._do_should_ignore(entry, root_dir, ignore_missing_files)
    except FileNotFoundError as ex:
      if ignore_missing_files:
        return True
      else:
        raise
  
  def _do_should_ignore(self, entry, root_dir, ignore_missing_files):
    root_dir = path.normpath(path.abspath(root_dir))

    self._log.log_d(f'should_ignore: entry="{entry.filename}" root_dir="{root_dir}"')

    if not self._ignore_filename:
      self._log.log_d(f'should_ignore: no ignore_filename given.')
      return False
    
    ignore_files = self._find_ignore_files(entry, root_dir)
    num = len(ignore_files)
    for i, next_ignore_file in enumerate(ignore_files, start = 1):
      self._log.log_d(f'should_ignore: next_ignore_file: {i} of {num}: {next_ignore_file}')
    for i, next_ignore_file in enumerate(ignore_files, start = 1):
      if self._do_should_ignore_one_item(next_ignore_file, entry, root_dir, i, num):
        return True
    return False

  def _do_should_ignore_one_item(self, ignore_file, entry, root_dir, i, num):
    item = self._get_ignore_item(ignore_file)
    should_ignore = item.should_ignore(entry)
    self._log.log_d(f'should_ignore:  checking {i} of {num}: "{entry.absolute_filename}" with "{ignore_file}" => {should_ignore}')
    return should_ignore
  
  def _find_ignore_files(self, entry, root_dir):
    assert entry.is_file
    decomposed_path = [ p for p in reversed(entry.decomposed_path) ]
    decomposed_path.pop(0)
    for i, next_path in enumerate(decomposed_path, start = 1):
      self._log.log_d(f'_find_ignore_files: decomposed_path:{i}: {next_path}')
    num = len(entry.decomposed_path)
    result = []
    for i, ancestor in enumerate(decomposed_path, start = 1):
      if not ancestor.startswith(root_dir):
        break
      next_ignore_filename = path.join(ancestor, self._ignore_filename)
      if path.exists(next_ignore_filename):
        result.append(next_ignore_filename)
    return result
  
  def _get_ignore_item(self, ignore_filename):
    if ignore_filename not in self._items:
      self._items[ignore_filename] = bf_file_ignore_item.read_file(ignore_filename)
    return self._items[ignore_filename]
  
  def filter_entries(self, entries, root_dir, ignore_missing_files = True):
    check.check_bf_entry_list(entries)
    check.check_string(root_dir)
    check.check_bool(ignore_missing_files)

    return [ e for e in entries if not self.should_ignore(entry, root_dir, ignore_missing_files = ignore_missing_files) ]

  
