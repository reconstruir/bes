#!/usr/bin/env python
#-*- coding:utf-8 -*-

import fnmatch
from .matcher_base import matcher_base
from bes.common import object_util

class matcher_filename(matcher_base):
  'Filename matcher using fnmatch.'

  def __init__(self, pattern, ignore_case = False):
    self._pattern = pattern
    self._ignore_case = ignore_case
    if self._ignore_case:
      self._pattern = self._pattern.lower()
      
  def match(self, text):
    if self._ignore_case:
      return fnmatch.fnmatch(text.lower(), self._pattern)
    else:
      return fnmatch.fnmatchcase(text, self._pattern)

  def __str__(self):
    return '(%s, %s)' % (self._pattern, self._ignore_case)

class matcher_multiple_filename(matcher_base):
  'Filename matcher using multiple filename matchers.'

  def __init__(self, patterns, ignore_case = False):
    patterns = object_util.listify(patterns)
    self._matchers = [ matcher_filename(pattern, ignore_case = ignore_case) for pattern in patterns ]
      
  def match(self, text):
    for matcher in self._matchers:
      if matcher.match(text):
        return True
    return False

  def __str__(self):
    return ', '.join([ str(m) for m in self._matchers ])
