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
      self._assign_line_token_seq(text)
    elif check.is_seq(text, tuple):
      tokens = [ line_token(*line) for line in text ]
      self._assign_line_token_seq(tokens)
    else:
      check.check_string(text)
      self._lines = self._parse(text, self._delimiter)
      self._ends_with_delimiter = text and text[-1] == self._delimiter

  def _assign_line_token_seq(self, tokens):
    check.check_line_token_seq(tokens)
    self._lines = []
    line_number = None
    for line in tokens:
      if line_number is not None:
        if line.line_number <= line_number:
          raise ValueError('line_number should be %d or greater instead of %d: \"%s\"' % (line_number + 1, line.line_number, line.text))
      self._lines.append(line)
      line_number = line.line_number
    self._ends_with_delimiter = False

  def __iter__(self):
    return iter(self._lines)
    
  def __str__(self):
    return self.to_string()
    
  def __repr__(self):
    return str(self)

  def __eq__(self, other):
    if isinstance(other, text_line_parser):
      return self._lines == other._lines
    elif check.is_line_token_seq(other):
      return self._lines == other
    elif check.is_seq(other, tuple):
      return self._lines == other
    else:
      raise TypeError('invalid type for __eq__: %s' % (type(other)))
  
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

  _match_result = namedtuple('_match_result', 'expression,match,line')
  def match_first(self, expressions, strip_comments = False, line_number = None):
    expressions = object_util.listify(expressions)
    for line in self._lines:
      if line_number is not None:
        if line.line_number < line_number:
          continue
      text = line.get_text(strip_comments = strip_comments)
      for expression in expressions:
        match = re.findall(expression, text)
        if match:
          return self._match_result(expression, match, line)
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
        match = re.findall(expression, text)
        if match:
          return self._match_result(expression, match, line)
    return None
  
  def match_all(self, expressions, strip_comments = False):
    expressions = object_util.listify(expressions)
    result = []
    for line in self._lines:
      text = line.get_text(strip_comments = strip_comments)
      for expression in expressions:
        if re.match(expression, text):
          result.append(line)
    return text_line_parser(result)

  def cut_lines(self, start_pattern, end_pattern, include_pattern = False, line_number = None):
    if not start_pattern and not end_pattern:
      raise ValueError('one or both of start_pattern and end_pattern need to be valid.')
    if start_pattern and end_pattern:
      return self._cut_lines_between(start_pattern, end_pattern, include_pattern, line_number)
    elif start_pattern:
      return self._cut_lines_after(start_pattern, include_pattern, line_number)
    elif end_pattern:
      return self._cut_lines_before(end_pattern, include_pattern, line_number)
    else:
      assert False

  @classmethod
  def GE(clazz, a, b):
    return a >= b
  
  @classmethod
  def LE(clazz, a, b):
    return a <= b

  @classmethod
  def GT(clazz, a, b):
    return a > b
  
  @classmethod
  def LT(clazz, a, b):
    return a < b

  @classmethod
  def _start_comparator(clazz, include_pattern):
    if include_pattern:
      return clazz.GE
    else:
      return clazz.GT

  @classmethod
  def _end_comparator(clazz, include_pattern):
    if include_pattern:
      return clazz.LE
    else:
      return clazz.LT
    
  def _cut_lines_after(self, start_pattern, include_pattern, line_number):
    head = self.match_first(start_pattern, line_number = line_number)
    if not head:
      return None
    comp = self._start_comparator(include_pattern)
    return text_line_parser([ line for line in self._lines if comp(line.line_number, head.line.line_number) ])
  
  def _cut_lines_before(self, end_pattern, include_pattern, line_number):
    tail = self.match_first(end_pattern, line_number = line_number)
    if not tail:
      return None
    comp = self._end_comparator(include_pattern)
    return text_line_parser([ line for line in self._lines if comp(line.line_number, tail.line.line_number) ])

  def _cut_lines_between(self, start_pattern, end_pattern, include_pattern, line_number):
    head = self.match_first(start_pattern, line_number = line_number)
    if not head:
      return None
    tail = self.match_first(end_pattern, line_number = head.line.line_number)
    if not tail:
      return None
    start_comp = self._start_comparator(include_pattern)
    end_comp = self._end_comparator(include_pattern)
    return text_line_parser([ line for line in self._lines if start_comp(line.line_number, head.line.line_number) and end_comp(line.line_number, tail.line.line_number) ])

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

  def cut_sections(self, start_pattern, end_pattern, include_pattern = False, line_number = None):
    result = []
    text = str(self)
    line_number = line_number or 1
    while True:
      lines = self.cut_lines(start_pattern, end_pattern, include_pattern = include_pattern, line_number = line_number)
      if not lines:
        break
      result.append(lines)
      line_number = lines[-1].line_number + 1
    return result
