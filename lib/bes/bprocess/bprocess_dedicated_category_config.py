# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..common.tuple_util import tuple_util

from .bprocess_priority import bprocess_priority

class bprocess_dedicated_category_config(namedtuple('bprocess_dedicated_category_config', 'num_processes, nice')):
  
  def __new__(clazz, num_processes, nice):
    check.check_int(num_processes)
    check.check_int(nice, allow_none = True)

    return clazz.__bases__[0].__new__(clazz, num_processes, nice)

  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
check.register_class(bprocess_dedicated_category_config, include_seq = False, cast_func = bprocess_dedicated_category_config._check_cast_func)
  
