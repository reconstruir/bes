#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import math
from bes.compat import StringIO
from collections import namedtuple

class _line(object):
  
  def __init__(self, line_number = None, text = None, continuation = '\\'):
    self.line_number = line_number
    self.text = text
    self.has_continuation = text.strip().endswith(continuation)

  def __str__(self):
    return '%s:%s' % (self.line_number, self.text)
    
  def __repr__(self):
    return str(self)
    
class lines(object):
  'Manage text as lines.'

  def __init__(self, text, delimiter = '\n', continuation = '\\'):
    self._original_text = text
    self._delimiter = delimiter
    self._continuation = continuation
    self._lines = self._parse(self._original_text, self._delimiter, self._continuation)
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
  def _parse(clazz, text, delimiter, continuation):
    lines = text.split(delimiter)
    range(1, len(lines) + 1)
    lines = [ _line(*item) for item in zip(range(1, len(lines) + 1), lines) ]
    conts = clazz._find_conts(lines)
    for cont in conts:
      print('CONT: %s' % (conts))
    return lines

  _conts = namedtuple('_conts', 'line_number,lines')
  @classmethod
  def _find_conts(clazz, lines):
    conts = []
    cont_lines = [ line for line in lines if line.has_continuation ]
    for cont_line in cont_lines:
      conts.append(clazz._find_cont_lines(lines, cont_line))
    return conts

  @classmethod
  def _find_cont_lines(clazz, lines, line):
    result = []
    assert line.has_continuation
    index = line.line_number - 1
    while line.has_continuation:
      result.append(line)
      index = index + 1
      if index == len(lines):
        break
      line = lines[index]
    result.append(line)
    return result
  
  def add_line_numbers(self, delimiter = '|'):
    width = math.trunc(math.log10(len(self._lines)) + 1)
    fmt  = '%%%dd' % (width)
    buf = StringIO()
    for line in self._lines:
      buf.write(fmt % (line.line_number))
      line_number_text = fmt % line.line_number
      line.text = '%s%s%s' % (line_number_text, delimiter, line.text)
    return buf.getvalue()
  
