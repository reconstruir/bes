# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check

from .btask_priority import btask_priority

class btask_config(namedtuple('btask_config', 'category, priority, limit, debug, timeout_seconds, kill_grace_seconds')):

  def __new__(clazz, category, priority = btask_priority.MEDIUM, limit = 3, debug = False,
              timeout_seconds = None, kill_grace_seconds = 5):
    check.check_string(category)
    priority = check.check_btask_priority(priority)
    check.check_int(limit)
    check.check_bool(debug)
    check.check_int(timeout_seconds, allow_none = True)
    check.check_int(kill_grace_seconds)

    if timeout_seconds is not None and timeout_seconds < 2:
      raise ValueError(f'timeout_seconds must be >= 2, got {timeout_seconds}')
    if kill_grace_seconds < 1:
      raise ValueError(f'kill_grace_seconds must be >= 1, got {kill_grace_seconds}')

    return clazz.__bases__[0].__new__(clazz, category, priority, limit, debug,
                                      timeout_seconds, kill_grace_seconds)

  @classmethod
  def _check_cast_func(clazz, obj):
    return clazz(*obj)

check.register_class(btask_config, include_seq = False, cast_func = btask_config._check_cast_func)
