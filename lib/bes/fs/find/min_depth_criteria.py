#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .criteria import criteria

class min_depth_criteria(criteria):
  'make sure the file path depth satisfies a min.'

  def __init__(self, min_depth):
    super(min_depth_criteria, self).__init__(action = FILTER, target = DIR)
    self.min_depth = min_depth
  
  def matches(self, variables):
    return variables.depth >= self.min_depth
