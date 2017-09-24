#!/usr/bin/env python
#-*- coding:utf-8 -*-

from object_util import object_util

class string_list(object):
  'string list helpers'

  @classmethod
  def remove_if(clazz, l, blacklist):
    'Remove any items in l that are present both in l and blacklist preserving order.'
    blacklist_set = set(blacklist)
    result = []
    for x in l:
      if x not in blacklist_set:
        result.append(x)
    return result

  @classmethod
  def is_string_list(clazz, l):
    'Return True if l is a homogenous string list.'
    return object_util.is_homogeneous(l, ( str, unicode ))
