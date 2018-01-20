#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import math
from bes.compat import StringIO

class _line(object):
  
  def __init__(self, line_number = None, text = None):
    self.line_number = line_number
    self.text = text

  def __str__(self):
    return '%s:%s' % (self.line_number, self.text)
    
class lines(object):
  'Manage text as lines.'

  def __init__(self, text, delimiter = '\n', continuation = '\\'):
    self._original_text = text
    self._delimiter = delimiter
    self._continuation = continuation
    self._lines = self._parse(self._original_text, self._delimiter, self._continuation)
    self._ends_with_delimiter = text and text[-1] == self._delimiter
    
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
    lines = {}
    buf = StringIO()
    line_number = 1
    max_line_number = 0
    for c in text:
      if c == delimiter:
        assert line_number not in lines
        lines[line_number] = _line(line_number, buf.getvalue())
        buf = StringIO()
        line_number = line_number + 1
        max_line_number = max(max_line_number, line_number)
      elif c == continuation:
        assert False
      else:
        buf.write(c)
    last_value = buf.getvalue()
    if last_value:
      assert line_number not in lines
      lines[line_number] = _line(line_number, last_value)
    max_line_number = max(max_line_number, 1)
    result = [ None ] * max_line_number
    for line in lines.values():
      result[line.line_number - 1] = line
    for i, line in enumerate(result):
      if not line:
        result[i] = _line(i + 1, '')
    return result

  '''
  def add_line_numbers(clazz, text, delimiter = '|'):
    lines = text.split('\n')
    width = math.trunc(math.log10(len(lines)) + 1)
    fmt  = '%%%dd' % (width)
    buf = StringIO()
    for line_number, line in zip(range(1, 1 + len(lines)), lines):
      buf.write(fmt % (line_number))
      buf.write(delimiter)
      buf.write(str(line))
      buf.write('\n')
    return buf.getvalue()
'''
  
