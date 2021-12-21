#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
import string
import sys

from bes.compat.StringIO import StringIO
from bes.system.compat import compat
from .check import check

class char_util(object):
  'Class for misc dealings with characters'

  _NOT_WORD_BOUNDARY_CHARS = {
    True: string.ascii_letters + string.digits,
    False: string.ascii_letters + string.digits + '_',
  }
  
  @classmethod
  def is_word_boundary(clazz, s, underscore = False):
    'Return True if s is a word boundary character.'
    return s not in clazz._NOT_WORD_BOUNDARY_CHARS[underscore]
