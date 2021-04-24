#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch
from .matcher_base import matcher_base
from bes.common.object_util import object_util

class matcher_filename(matcher_base):
  'Filename matcher using fnmatch.'

  def __init__(self, pattern, ignore_case = False):
    self._pattern = pattern
    self._ignore_case = ignore_case
    if self._ignore_case:
      self._pattern = self._pattern.lower()
    self._escaped_pattern = self._escape_pattern(self._pattern)
      
  def match(self, text):
    if self._ignore_case:
      match_text = text.lower()
      func = fnmatch.fnmatch
    else:
      match_text = text
      func = fnmatch.fnmatchcase
    result = func(match_text, self._escaped_pattern)
    if False:
      print('match: text="{}" match-text="{}" pattern="{}" func={} => {}'.format(text,
                                                                                 match_text,
                                                                                 self._escaped_pattern,
                                                                                 func,
                                                                                 result))
    return result

  def __str__(self):
    return '({}, {})'.format(self._pattern, self._ignore_case)

  @classmethod
  def _escape_pattern(clazz, pattern):
    # In python 3 could use glob.escape() for a more complete escape strategy
    return pattern.replace('[', '[[]')
  
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
