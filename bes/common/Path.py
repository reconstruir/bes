#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path as path, os

class Path(object):
  'Path'
  @classmethod
  def is_executable(clazz, p):
    'Return True if the path is executable.'
    return path.exists(p) and os.access(p, os.X_OK)
