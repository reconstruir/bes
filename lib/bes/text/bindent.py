#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from ..compat.StringIO import StringIO
from ..system.check import check

class bindent(object):
  'Deal with indenting text.'
      
  @classmethod
  def indent(clazz, text, width):
    check.check_string(text)
    check.check_int(width)

    end = os.linesep if text and text[-1] == os.linesep else ''
    head = ' ' * width
    result_lines = [ f'{head}{line}' for line in text.splitlines(keepends = False) ]
    return os.linesep.join(result_lines) + end
