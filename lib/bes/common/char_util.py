#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
import string
import sys

from ..compat.StringIO import StringIO
from ..system.compat import compat
from ..system.check import check

class char_util(object):
  'Class for misc dealings with characters'

  _NOT_WORD_BOUNDARY_CHARS = {
    True: string.ascii_letters + string.digits,
    False: string.ascii_letters + string.digits + '_',
  }
  
  @classmethod
  def is_word_boundary(clazz, c, underscore = False):
    'Return True if s is a word boundary character.'
    assert len(c) == 1
    
    return c not in clazz._NOT_WORD_BOUNDARY_CHARS[underscore]

  @classmethod
  def is_punctuation(clazz, c):
    'Return True if c is punctuation.'
    assert len(c) == 1
    return c in string.punctuation
  
