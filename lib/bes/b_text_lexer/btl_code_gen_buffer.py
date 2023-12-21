#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import io
from ..system.check import check
from ..text.bindent import bindent

class btl_code_gen_buffer(object):

  def __init__(self, indent_width = 2):
    self._indent_width = indent_width
    self._current_indent_depth = 0
    self._buffer = io.StringIO()

  def get_value(self, indent_width = 0, eof_line_sep = True):
    check.check_int(indent_width)

    value = self._buffer.getvalue()
    if eof_line_sep and not value.endswith(os.linesep):
      value += os.linesep
    if indent_width == 0:
      return value
    return bindent.indent(value, indent_width)

  def write(self, s, indent_depth = 0):
    check.check_string(s)
    check.check_int(indent_depth)

    self._buffer.write(self._indent_spaces(indent_depth))
    self._buffer.write(s)

  def write_line(self, s, indent_depth = 0):
    check.check_string(s)
    check.check_int(indent_depth)

    self.write(s, indent_depth = indent_depth)
    self.write(os.linesep)

  def _indent_spaces(self, indent_depth):
    total_indent_depth = self._current_indent_depth + indent_depth
    indent_spaces = ' ' * (total_indent_depth * self._indent_width)
    return indent_spaces
