#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..version.semantic_version import semantic_version

class btl_header(namedtuple('btl_header', 'name, description, version, start_state, end_state')):
  
  def __new__(clazz, name, description, version, start_state, end_state):
    check.check_string(name)
    check.check_string(description)
    version = check.check_semantic_version(version)
    check.check_string(start_state)
    check.check_string(end_state)
    return clazz.__bases__[0].__new__(clazz, name, description, version, start_state, end_state)

check.register_class(btl_header)
