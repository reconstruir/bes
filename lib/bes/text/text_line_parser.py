#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import math
from bes.compat import StringIO
from collections import namedtuple
from .line_token import line_token
from .line_continuation_merger import line_continuation_merger
from .string_list import string_list

class text_line_parser(object):
  'Manage text as lines.'

  def __init__(self, text, delimiter = '\n'):
    self._delimiter = delimiter
    self._lines = self._parse(text, self._delimiter)
    self._ends_with_delimiter = text and text[-1] == self._delimiter

  def __str__(self):
    return self.to_string()
    
  def __repr__(self):
    return str(self)
    
  def to_string(self, strip_comments = False):
    buf = StringIO()
    for line in self._lines:
      buf.write(line.get_text(no_comments = strip_comments))
      buf.write(self._delimiter)
    v = buf.getvalue()
    if self._ends_with_delimiter:
      if v and v[-1] != self._delimiter:
        buf.write(self._delimiter)
    else:
      if v and v[-1] == self._delimiter:
        v = v[0:-1]
    return v
    
  def to_string_list(self, strip_comments = False):
    sl = string_list()
    for line in self._lines:
      sl.append(line.get_text(no_comments = strip_comments))
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

  @classmethod
  def parse_lines(clazz, text, strip_comments = True, strip_text = True, remove_empties = True):
    l = text_line_parser(text).to_string_list(strip_comments = strip_comments)
    if strip_text:
      l.strip()
    if remove_empties:
      l.remove_empties()
    return l

#  @classmethod
#  def add_line_numbers(clazz, text, delimiter = '|'):
#    l = text_line_parser(text)
#    l.add_line_numbers(delimiter = delimiter)
#    return str(l)

  @classmethod
  def find_line_with_re(clazz, expression, no_comments = False):
    for line in self._lines:
      if re.match(expression, line.get_text(no_comments = no_comments)):
        return line
    return None
