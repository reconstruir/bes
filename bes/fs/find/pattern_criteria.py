#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .criteria import criteria
import fnmatch

class pattern_criteria(criteria):
  'match the file type.'

  def __init__(self, pattern, action = criteria.FILTER):
    super(pattern_criteria, self).__init__(action = action, target = self.ANY)
    self.pattern = pattern
  
  def matches(self, variables):
    return fnmatch.fnmatch(variables.filename, self.pattern)
