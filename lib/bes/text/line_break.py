#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.host import host

class line_break(object):
  'Deal with line breaks.'

  # str.splitlines() uses these as line break delimiters
  LINE_BREAKS = [ 
    '\r\n',    # Carriage Return + Line Feed
    '\n',      # Line Feed
    '\r',      # Carriage Return
    '\v',      # or \x0b	Line Tabulation
    '\f',      # or \x0c	Form Feed
    '\x1c',    # File Separator
    '\x1d',    # Group Separator
    '\x1e',    # Record Separator
#    '\x85',   # Next Line (C1 Control Code)
    '\u2028',  # Line Separator
    '\u2029',  # Paragraph Separator
  ]

  LINE_BREAKS_SET = set(LINE_BREAKS)

  if host.is_unix():
    DEFAULT_LINE_BREAK = '\n'
    DEFAULT_LINE_BREAK_RAW = r'\n'
  else:
    DEFAULT_LINE_BREAK = '\r\n'
    DEFAULT_LINE_BREAK_RAW = r'\r\n'

  @classmethod
  def is_line_break(clazz, c):
    'return true if c is a line break'
    return c in clazz.LINE_BREAKS_SET
  
  @classmethod
  def ends_with_line_break(clazz, s):
    'Return True if s ends with a line break'
    return clazz.is_line_break(s[-1])

  @classmethod
  def guess_line_break(clazz, s):
    'Guess the line break for a multi line string or None if not multi line.'
    for lb in clazz.LINE_BREAKS:
      if lb in s:
        return lb
    return None
