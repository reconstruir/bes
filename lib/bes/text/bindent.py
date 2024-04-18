#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from ..compat.StringIO import StringIO
from ..system.check import check

class bindent(object):
  'Deal with indenting text.'
      
  @classmethod
  def indent(clazz, text, indent_width, fix_empty_lines = True):
    check.check_string(text)
    check.check_int(indent_width)
    check.check_bool(fix_empty_lines)

    header = ' ' * indent_width
    lines = text.splitlines(keepends = False)
    indented_lines = [ clazz._indent_line(line, header, fix_empty_lines) for line in lines ]
    end = os.linesep if text and text.endswith(os.linesep) else ''
    return os.linesep.join(indented_lines) + end

  @classmethod
  def _indent_line(clazz, line, header, fix_empty_lines):
    if not line:
      return ''
    if fix_empty_lines and line.isspace():
      return ''
    return f'{header}{line}'
