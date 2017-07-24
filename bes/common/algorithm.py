#!/usr/bin/env python
#-*- coding:utf-8 -*-

class algorithm(object):
  'algorithm'

  @staticmethod
  def remove_empties(l, recurse = True):
    'Return a list of the non empty items in l'
    assert isinstance(l, list)
    def is_empty(x):
      return x in [ (), [], None, '' ]
    result = [ x for x in l if not is_empty(x) ]
    for i in range(0, len(result)):
      if isinstance(result[i], list):
        result[i] = algorithm.remove_empties(result[i])
    return result

  @classmethod
  def unique(clazz, l):
    'Return a unique version of the list maintaining order.'
    result = []
    seen = set()
    for i in l:
      if i not in seen:
        result.append(i)
        seen.add(i)
    return result

