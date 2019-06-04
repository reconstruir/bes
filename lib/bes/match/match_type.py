#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class match_type(object):
  ANY = 1
  NONE = 2
  ALL = 3

  VALID_TYPES = [ ANY, NONE, ALL ]

  @classmethod
  def is_valid(clazz, match_type):
    return match_type in clazz.VALID_TYPES
