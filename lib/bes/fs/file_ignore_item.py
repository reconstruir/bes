#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from os import path

from ..system.check import check
from bes.text.text_line_parser import text_line_parser

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
