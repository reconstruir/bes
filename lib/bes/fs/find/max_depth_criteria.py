#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .criteria import criteria

class max_depth_criteria(criteria):
  'make sure the file path depth is less than or equal to a max depth.'

  def __init__(self, max_depth):
    super(max_depth_criteria, self).__init__(action = self.STOP, target = self.DIR)
    self.max_depth = max_depth
  
  def matches(self, variables):
    return variables.depth <= self.max_depth
