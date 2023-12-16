#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..version.semantic_version import semantic_version

class btl_desc_error(namedtuple('btl_desc_error', 'name, message')):
  
  def __new__(clazz, name, message):
    check.check_string(name)
    check.check_string(description)
    return clazz.__bases__[0].__new__(clazz, name, message)

check.register_class(btl_desc_error)
