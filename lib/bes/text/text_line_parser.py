#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import math, re
from bes.common import algorithm, check, object_util
from bes.compat import StringIO, cmp
from collections import namedtuple
from .line_token import line_token
from .line_continuation_merger import line_continuation_merger
from .string_list import string_list

class text_line_parser(object):
  'Manage text as lines.'

  def __init__(self, text, delimiter = '\n'):
    self._delimiter = delimiter
    if isinstance(text, text_line_parser):
      self._lines = text._lines[:]
      self._ends_with_delimiter = False
    elif check.is_line_token_seq(text):
      self._lines = [ line for line in text ]
      self._ends_with_delimiter = False
    elif check.is_seq(text, tuple):
      self._lines = [ line_token(*line) for line in text ]
      self._ends_with_delimiter = False
    else:
      check.check_string(text)
      self._lines = self._parse(text, self._delimiter)
      self._ends_with_delimiter = text and text[-1] == self._delimiter

  def __iter__(self):
    return iter(self._lines)
    
  def __str__(self):
    return self.to_string()
    
  def __repr__(self):
    return str(self)
    
  def to_string(self, strip_comments = False):
    buf = StringIO()
    for line in self._lines:
      buf.write(line.get_text(strip_comments = strip_comments))
      buf.write(self._delimiter)
    v = buf.getvalue()
    if self._ends_with_delimiter:
      if v and v[-1] != self._delimiter:
        buf.write(self._delimiter)
    else:
      if v and v[-1] == self._delimiter:
        v = v[0:-1]
    return v
    
  def to_string_list(self, strip_comments = False, strip_text = False):
    sl = string_list()
    for line in self._lines:
      sl.append(line.get_text(strip_comments = strip_comments, strip_text = strip_text))
    return sl
    
  def __len__(self):
    return len(self._lines)

  def __getitem__(self, n):
    return self._lines[n]

  def __setitem__(self, n, v):
    raise RuntimeError('lines are read only.')

  @classmethod
  def _parse(clazz, text, delimiter):
    lines = text.split(delimiter)
    range(1, len(lines) + 1)
    lines = [ line_token(*item) for item in zip(range(1, len(lines) + 1), lines) ]
    return lines

  def add_line_numbers(self, delimiter = '|'):
    width = math.trunc(math.log10(len(self._lines)) + 1)
    fmt  = '%%%dd' % (width)
    for i, line in enumerate(self._lines):
      line_number_text = fmt % line.line_number
      text = '%s%s%s' % (line_number_text, delimiter, line.text)
      self._lines[i] = line_token(line.line_number, text)
  
  def prepend(self, s):
    for i, line in enumerate(self._lines):
      self._lines[i] = line_token(line.line_number, '%s%s' % (s, line.text))
  
  def append(self, s):
    for i, line in enumerate(self._lines):
      self._lines[i] = line_token(line.line_number, '%s%s' % (line.text, s))
  
  def merge_continuations(self):
    self._lines = line_continuation_merger.merge_to_list(self._lines)

  def texts(self, strip_head = False, strip_tail = False):
    def _do_strip(s):
      if strip_head and strip_tail:
        return s.strip()
      elif strip_head:
        return s.lstrip()
      elif strip_tail:
        return s.rstrip()
    return [ _do_strip(line.text) for line in self._lines ]

#  @classmethod
#  def read_file(clazz, filename):
#    with open(filename, 'r') as f:
#      return clazz(f.read())

  def remove_empties(self):
    self._lines = [ line for line in self._lines if not line.text_is_empty() ]

  def strip(self):
    self._lines = [ line.clone_stripped() for line in self._lines ]

  @classmethod
  def parse_lines(clazz, text, strip_comments = True, strip_text = True, remove_empties = True):
    l = text_line_parser(text).to_string_list(strip_comments = strip_comments, strip_text = strip_text)
    if remove_empties:
      l.remove_empties()
    return l

#  @classmethod
#  def add_line_numbers(clazz, text, delimiter = '|'):
#    l = text_line_parser(text)
#    l.add_line_numbers(delimiter = delimiter)
#    return str(l)

  def match_first(self, expressions, strip_comments = False):
    expressions = object_util.listify(expressions)
    for line in self._lines:
      text = line.get_text(strip_comments = strip_comments)
      for expression in expressions:
        if re.match(expression, text):
          return line
    return None

  def match_backwards(self, line_number, expressions, strip_comments = False):
    expressions = object_util.listify(expressions)
    start_index = self.find_by_line_number(line_number) - 1
    if start_index < 0:
      return None
    for i in range(start_index, -1, -1):
      line = self._lines[i]
      text = line.get_text(strip_comments = strip_comments)
      for expression in expressions:
        if re.match(expression, text):
          return line
    return None
  
  def match_all(self, expressions, strip_comments = False):
    expressions = object_util.listify(expressions)
    result = []
    for line in self._lines:
      text = line.get_text(strip_comments = strip_comments)
      for expression in expressions:
        if re.match(expression, text):
          result.append(line)
    return result

  def find_line_with_re(self, expressions, strip_comments = False):
    expressions = object_util.listify(expressions)
    for line in self._lines:
      text = line.get_text(strip_comments = strip_comments)
      for expression in expressions:
        f = re.findall(expression, text)
        if f:
          return f
    return None
  
  def cut_lines(self, start_pattern, end_pattern):
    if not start_pattern and not end_pattern:
      raise ValueError('one or both of start_pattern and end_pattern need to be valid.')
    if start_pattern and end_pattern:
      return self._cut_lines_between(start_pattern, end_pattern)
    elif start_pattern:
      return self._cut_lines_after(start_pattern)
    elif end_pattern:
      return self._cut_lines_before(end_pattern)
    else:
      assert False

  def _cut_lines_after(self, start_pattern):
    head = self.match_first(start_pattern)
    if not head:
      return None
    new_lines = text_line_parser('')
    new_lines._lines = [ line for line in self._lines if line.line_number > head.line_number ]
    return new_lines
  
  def _cut_lines_before(self, end_pattern):
    tail = self.match_first(end_pattern)
    if not tail:
      return None
    new_lines = text_line_parser('')
    new_lines._lines = [ line for line in self._lines if line.line_number < tail.line_number ]
    return new_lines

  def _cut_lines_between(self, start_pattern, end_pattern):
    head = self.match_first(start_pattern)
    if not head:
      return None
    tail = self.match_first(end_pattern)
    if not tail:
      return None
    new_lines = text_line_parser('')
    new_lines._lines = [ line for line in self._lines if line.line_number > head.line_number and line.line_number < tail.line_number ]
    return new_lines

  def find_by_line_number(self, line_number):
    target = line_token(line_number, '')
    return algorithm.binary_search(self._lines, target, self._line_number_comparator)
  
  @staticmethod
  def _line_number_comparator(line1, line2):
    return cmp(line1.line_number, line2.line_number)
    
  def remove_line_number(self, line_number):
    i = self.find_by_line_number(line_number)
    if i >= 0:
      result = self._lines[i]
      del self._lines[i]
      return result
    return None
      
  def combine_lines(self, line_number1, line_number2, delimiter = ' '):
    index1 = self.find_by_line_number(line_number1)
    if index1 < 0:
      raise IndexError('invalid line number 1: %s' % (line_number1))
    line1 = self._lines[index1]
    index2 = self.find_by_line_number(line_number2)
    if index2 < 0:
      raise IndexError('invalid line number 2: %s' % (line_numdber2))
    line2 = self._lines[index2]
    del self._lines[index2]
    new_text = '%s%s%s' % (line1.text, delimiter, line2.text)
    new_line = line_token(line1.line_number, new_text)
    self._lines[index1] = new_line
