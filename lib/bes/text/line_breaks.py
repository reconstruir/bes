#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class line_breaks(object):
  'Add line numbers to text.'

  # str.splitlines uses these are line break delimiters
  DELIMITERS = { 
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
    return s[-1] in clazz.DELIMITERS
