#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path as path, re

from bes.common import algorithm, object_util, string_util
from bes.common import check
from .file_find import file_find
from .file_replace import file_replace
from .file_util import file_util
from collections import namedtuple

class file_search(object):

  class search_item(namedtuple('search_item', 'filename,line_number,pattern,line,span')):

    def __new__(clazz, filename, line_number, pattern, line,span):
      return clazz.__bases__[0].__new__(clazz, filename, line_number, pattern, line, span)

    def become_relative(self, root_dir):
      return self.__class__(file_util.remove_head(self.filename, root_dir),
                            self.line_number, self.pattern, self.line, self.span)
  span = namedtuple('span', 'start,end')

  @classmethod
  def search(clazz, root_dir, text, relative = True, min_depth = None, max_depth = None):
    check.check_string(root_dir)
    #assert string_util.is_string(text)
    files = file_find.find(root_dir, relative = relative, min_depth = min_depth, max_depth = max_depth)
    items = []
    for f in files:
      fpath = path.join(root_dir, f)
      next_items = clazz.search_file(fpath, text)
      items += next_items
    if relative:
      return [ item.become_relative(root_dir) for item in items ]
    return items

  @classmethod
  def search_file(clazz, filename, text, word_boundary = False, ignore_case = False):
    #assert string_util.is_string(text)
    try:
      content = file_util.read(filename, 'utf-8')
    except UnicodeDecodeError as ex:
      return []
    result = clazz.search_string(content, text, word_boundary = word_boundary, ignore_case = ignore_case)
    return [ clazz.search_item(filename, item.line_number, item.pattern, item.line, item.span) for item in result ]

  @classmethod
  def search_string(clazz, content, patterns, word_boundary = False, ignore_case = False):
    assert string_util.is_string(content)
    patterns = object_util.listify(patterns)
    result = []
    original_patterns = None
    if word_boundary:
      original_patterns = patterns[:]
      patterns = [ clazz._make_expresion(p, ignore_case) for p in patterns ]
    else:
      if ignore_case:
        original_patterns = patterns[:]
        patterns = [ p.lower() for p in patterns ]
    original_patterns = original_patterns or patterns
    patterns = list(zip(patterns, original_patterns))
    for line_number, line in enumerate(content.split('\n'), 1):
      if word_boundary:
        result += clazz._search_line_with_re(line, patterns, '<unknown>', line_number)
      else:
        result += clazz._search_line_with_find(line, patterns, '<unknown>', line_number, ignore_case)
    return result

  @classmethod
  def _make_expresion(clazz, text, ignore_case):
    flags = 0
    if ignore_case:
      flags = re.IGNORECASE
    return re.compile(r'\b%s\b' % (re.escape(text)), flags = flags)

  @classmethod
  def _search_line_with_find(clazz, line, patterns, filename, line_number, ignore_case):
    check.check_list(patterns)
    assert len(patterns) > 0
    
    result = []
    original_line = line
    if ignore_case:
      line = line.lower()
    for pattern, original_pattern in patterns:
      check.check_string(pattern)
      check.check_string(original_pattern)
      index = line.find(pattern)
      if index >= 0:
        span = clazz.span(index, index + len(pattern))
        result.append(clazz.search_item(filename, line_number, original_pattern, original_line, span))
    return result

  @classmethod
  def _search_line_with_re(clazz, line, patterns, filename, line_number):
    assert len(patterns) > 0
    result = []
    original_line = line
    line = re.escape(line)
    # when line gets escaped it can grow.  in order for the span to make sense
    # we need to take the delta in length between the escaped and original lines
    line_length_delta = len(line) - len(original_line)
    for pattern, original_pattern in patterns:
      for iter in pattern.finditer(line):
        span = iter.span()
        span = clazz.span(span[0]  - line_length_delta, span[1] - line_length_delta)
        result.append(clazz.search_item(filename, line_number, original_pattern, original_line, span))
    return result

  @classmethod
  def search_replace(clazz, root_dir, replacements, backup = True, test_func = None):
    assert isinstance(replacements, dict)
    text = [ str(x) for x in replacements.keys() ]
    items = clazz.search(root_dir, text, relative = False)
    filenames = algorithm.unique([ item.filename for item in items ])
    return file_replace.replace_many(filenames, replacements, backup = backup, test_func = test_func)
