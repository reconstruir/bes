#!/usr/bin/env python
#-*- coding:utf-8 -*-

import re

from .matcher_base import matcher_base

class matcher_always_true(matcher_base):
  'A matcher that always returns True.'

  def __init__(self):
    pass

  def match(self, text, ignore_case = False):
    return True
