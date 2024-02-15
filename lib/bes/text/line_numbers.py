#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import math
from bes.compat.StringIO import StringIO

class line_numbers(object):
  'Add line numbers to text.'
      
  @classmethod
  def add_line_numbers(clazz, text, delimiter = '|'):
    lines = text.splitlines()
    width = math.trunc(math.log10(len(lines)) + 1)
    fmt  = '%%%dd' % (width)
    buf = StringIO()
    for line_number, line in zip(range(1, 1 + len(lines)), lines):
      buf.write(fmt % (line_number))
      buf.write(delimiter)
      buf.write(str(line))
      buf.write(os.linesep)
    return buf.getvalue()
