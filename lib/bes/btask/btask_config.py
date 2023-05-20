# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..common.tuple_util import tuple_util

from .btask_priority import btask_priority

class btask_config(namedtuple('btask_config', 'category, priority, limit, debug')):
  
  def __new__(clazz, category, priority = btask_priority.MEDIUM, limit = 3, debug = False):
    check.check_string(category)
    priority = check.check_btask_priority(priority)
    check.check_int(limit)
    check.check_bool(debug)

    return clazz.__bases__[0].__new__(clazz, category, priority, limit, debug)

  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
check.register_class(btask_config, include_seq = False, cast_func = btask_config._check_cast_func)
  
