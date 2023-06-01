# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..common.tuple_util import tuple_util

from .bprocess_priority import bprocess_priority

class bprocess_config(namedtuple('bprocess_config', 'category, priority, limit, debug')):
  
  def __new__(clazz, category, priority = bprocess_priority.MEDIUM, limit = 3, debug = False):
    check.check_string(category)
    priority = check.check_bprocess_priority(priority)
    check.check_int(limit)
    check.check_bool(debug)

    return clazz.__bases__[0].__new__(clazz, category, priority, limit, debug)

  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
check.register_class(bprocess_config, include_seq = False, cast_func = bprocess_config._check_cast_func)
  
