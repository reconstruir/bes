#!/usr/bin/env python
#-*- coding:utf-8 -*-

import math
from io import StringIO

class line_numbers(object):
  'Add line numbers to text.'
      
  @classmethod
  def add_line_numbers(clazz, text, delimiter = '|'):
    lines = text.split('\n')
    width = math.trunc(math.log10(len(lines)) + 1)
    format  = '%%%dd' % (width)
    buf = StringIO()
    for line_number, line in zip(range(1, 1 + len(lines)), lines):
      buf.write(unicode(format % (line_number)))
      buf.write(unicode(delimiter))
      buf.write(unicode(line))
      buf.write(u'\n')
    return buf.getvalue()
