#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import io

from ..system.check import check
from ..text.bindent import bindent

from .btl_code_gen_error import btl_code_gen_error

class btl_code_gen_buffer(object):

  def __init__(self, indent_width = 2, space_char = ' '):
    self._indent_width = indent_width
    self._indent_depth = 0
    self._space_char = space_char
    self._buffer = io.StringIO()

  @property
  def indent_width(self):
    return self._indent_width

  @property
  def indent_depth(self):
    return self._indent_depth

  @property
  def indent_spaces(self):
    return self._space_char * (self._indent_depth * self._indent_width)
  
  def get_value(self, indent_width = 0, eof_line_sep = False):
    check.check_int(indent_width)
    check.check_bool(eof_line_sep)

    if indent_width < 0:
      raise btl_code_gen_error(f'indent_width should be >= 0')
    
    value = self._buffer.getvalue()
    if eof_line_sep and not value.endswith(os.linesep):
      value += os.linesep
    if indent_width == 0:
      return value
    return bindent.indent(value, indent_width)

  def write(self, s):
    check.check_string(s)

    self._buffer.write(s)

  def write_line(self, s):
    check.check_string(s)

    self.write(self.indent_spaces)
    self.write(s)
    self.write(os.linesep)

  def write_lines(self, s):
    check.check_string(s)

    lines = s.splitlines()
    for line in lines:
      self.write_line(line)
    
  def push_indent(self):
    self._indent_depth += 1
  
  def pop_indent(self):
    if self._indent_depth == 0:
      raise btl_code_gen_error(f'Current indent depth is already 0')
    self._indent_depth -= 1

  class _indent_pusher(object):

    def __init__(self, buf):
      check.check_btl_code_gen_buffer(buf)
      self._buf = buf
    
    def __enter__(self):
      self._buf.push_indent()
      return self
  
    def __exit__(self, exception_type, exception_value, traceback):
      self._buf.pop_indent()
      return False

  def indent_pusher(self):
    return self._indent_pusher(self)
    
check.register_class(btl_code_gen_buffer, include_seq = False)
