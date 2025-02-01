#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from os import path

from bes.system.check import check
from bes.text.text_line_parser import text_line_parser
from bes.property.cached_property import cached_property

from ..bf_file_ops import bf_file_ops
from ..bf_entry import bf_entry
from ..match.bf_file_matcher import bf_file_matcher
from ..match.bf_file_matcher_type import bf_file_matcher_type

class bf_file_ignore_item(namedtuple('bf_file_ignore_item', 'directory, patterns')):

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
    return bf_file_matcher(patterns = self.patterns)
  
  def should_ignore(self, entry):
    check.check_bf_entry(entry)
    
    if not self.patterns:
      return False
    return self._matcher.match(entry)
  
