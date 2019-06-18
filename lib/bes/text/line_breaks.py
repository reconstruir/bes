#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class line_breaks(object):
  'Deal with line breaks.'

  # str.splitlines() uses these as line break delimiters
  LINE_BREAKS = { 
    '\n',      # Line Feed
    '\r',      # Carriage Return
    '\r\n',    # Carriage Return + Line Feed
    '\v',      # or \x0b	Line Tabulation
    '\f',      # or \x0c	Form Feed
    '\x1c',    # File Separator
    '\x1d',    # Group Separator
    '\x1e',    # Record Separator
    '\x85',    # Next Line (C1 Control Code)
    '\u2028',  # Line Separator
    '\u2029 ', # Paragraph Separator
  }
  
  @classmethod
  def ends_with_line_break(clazz, s):
    'Return True if s ends with a line break'
    return s[-1] in clazz.LINE_BREAKS

  @classmethod
  def is_line_break(clazz, c):
    'Return True if c is a line break'
    return c in clazz.LINE_BREAKS
  
