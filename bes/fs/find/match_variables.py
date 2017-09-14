#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

class match_variables(namedtuple('match_variables', 'depth,root_dir,filename,filepath')):

  def __new__(clazz, depth, root_dir, filename, filepath):
    return clazz.__bases__[0].__new__(clazz, depth, root_dir, filename, filepath)
