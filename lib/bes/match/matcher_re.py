#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from .matcher_base import matcher_base

class matcher_re(matcher_base):
  'Regular expression matcher.'

  def __init__(self, pattern, ignore_case = False):
    flags = 0
    if ignore_case:
      flags |= re.IGNORECASE
    self._expression = re.compile(pattern, flags)

  def match(self, text, ignore_case = False):
    return len(self._expression.findall(text)) > 0
