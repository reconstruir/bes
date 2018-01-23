#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import math
from bes.compat import StringIO
from collections import namedtuple
from .line_token import line_token
from .line_continuation_merger import line_continuation_merger

class lines(object):
  'Manage text as lines.'

  def __init__(self, text, delimiter = '\n'):
    self._original_text = text
    self._delimiter = delimiter
    self._lines = self._parse(self._original_text, self._delimiter)
    self._ends_with_delimiter = text and text[-1] == self._delimiter

  def __str__(self):
    buf = StringIO()
    for line in self._lines:
      buf.write(line.text)
      buf.write(self._delimiter)
    v = buf.getvalue()
    if self._ends_with_delimiter and v and v[-1] != self._delimiter:
      buf.write(self._delimiter)
    return buf.getvalue()
    
  def __len__(self):
    return len(self._lines)

  def __getitem__(self, n):
    if not self._line_number_is_valid(n):
      raise IndexError('line number should be [%s to %s] instead of: %s' % (1, self._num_lines + 1, n))
    return self._lines[n].text

  def __setitem__(self, n, v):
    raise RuntimeError('lines are read only.')

  def _line_number_is_valid(self, n):
    if n < 0:
      return False
    if n > len(self._lines):
      return False
    return True

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
  
  def merge_continuations(self):
    self._lines = line_continuation_merger.merge_to_list(self._lines)

  @classmethod
  def read_file(clazz, filename):
    with open(filename, 'r') as f:
      return clazz(f.read())
