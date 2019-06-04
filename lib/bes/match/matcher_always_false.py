#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from .matcher_base import matcher_base

class matcher_always_false(matcher_base):
  'A matcher that always returns False.'

  def __init__(self):
    pass

  def match(self, text, ignore_case = False):
    return False
