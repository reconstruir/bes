#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from os import path

from bes.system.check import check
from bes.text.text_line_parser import text_line_parser
from bes.property.cached_property import cached_property
from bes.system.log import logger

from ..bf_entry import bf_entry
from ..bf_file_ops import bf_file_ops
from ..bf_filename import bf_filename
from ..match.bf_file_matcher import bf_file_matcher
from ..match.bf_file_matcher_mode import bf_file_matcher_mode

class bf_file_ignore_item(namedtuple('bf_file_ignore_item', 'directory, patterns')):

  _log = logger('bf_file_ignore')
  
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
    text = bf_file_ops.read_text(filename, encoding = 'utf-8')
    patterns = text_line_parser.parse_lines(text).to_list()
    return bf_file_ignore_item(path.dirname(filename), patterns)

  @cached_property
  def _matcher(self):
    if not self.patterns:
      return None
    return bf_file_matcher(patterns = self.patterns)
  
  def should_ignore(self, entry, root_dir):
    check.check_bf_entry(entry)
    check.check_string(root_dir)
    
    if not self._matcher:
      return False
    num = len(self.patterns)
    for i, pattern in enumerate(self.patterns, start = 1):
      self._log.log_d(f'item should_ignore: pattern {i} of {num}: {pattern}')
    item_dir_relative = bf_filename.remove_head(self.directory, root_dir)
    entry_relative_filename = entry.filename_without_head(root_dir)
    entry_relative_to_item = entry.filename_without_head(path.join(root_dir, item_dir_relative))
    #self._log.log_d(f'item should_ignore: entry.filename="{entry.filename}"')
    #self._log.log_d(f'item should_ignore: item.directory="{item_dir_relative}"')
    #self._log.log_d(f'item should_ignore: entry.filename="{entry.filename}"')
    #self._log.log_d(f'item should_ignore: entry_relative_filename="{entry_relative_filename}"')
    #self._log.log_d(f'item should_ignore: entry_relative_to_item="{entry_relative_to_item}"')

    match_entries = [
      entry,
      bf_entry(entry_relative_to_item),
      bf_entry(entry_relative_to_item.split(path.sep)[0]),
    ]
    return self._matcher.match_entries(match_entries)
