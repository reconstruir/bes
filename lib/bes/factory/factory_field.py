#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from collections import namedtuple

class factory_field(namedtuple('factory_field', 'key, optional, checker_function')):
  def __new__(clazz, key, optional = False, checker_function = None):
    check.check_string(key)
    check.check_bool(optional)
    check.check_function(checker_function, allow_none = True)
    return clazz.__bases__[0].__new__(clazz, key, optional, checker_function)
