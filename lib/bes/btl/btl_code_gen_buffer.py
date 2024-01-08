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

  def write_linesep(self):
    self.write(os.linesep)
      
  def push_indent(self, depth = 1):
    self._indent_depth += depth
  
  def pop_indent(self, depth = 1):
    self._indent_depth -= depth
    if self._indent_depth < 0:
      raise btl_code_gen_error(f'Current indent depth popping underflow')

  class _indent_pusher(object):

    def __init__(self, buf, depth = 1):
      check.check_btl_code_gen_buffer(buf)
      self._depth = depth
      self._buf = buf
    
    def __enter__(self):
      self._buf.push_indent(depth = self._depth)
      return self
  
    def __exit__(self, exception_type, exception_value, traceback):
      self._buf.pop_indent(depth = self._depth)
      return False

  def indent_pusher(self, depth = 1):
    return self._indent_pusher(self, depth = depth)
    
check.register_class(btl_code_gen_buffer, include_seq = False)
