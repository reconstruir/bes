#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..common.string_util import string_util
from ..common.tuple_util import tuple_util
from ..system.check import check

class mmd_transition(namedtuple('mmd_transition', 'line, from_state, to_state, event')):

  def __new__(clazz, line, from_state, to_state, event):
    check.check_string(line)
    check.check_string(from_state)
    check.check_string(to_state)
    check.check_string(event)

    if to_state == '[*]':
      to_state = '__end'
    if from_state == '[*]':
      from_state = '__start'
    
    return clazz.__bases__[0].__new__(clazz, line, from_state, to_state, event)

  def to_dict(self):
    d = dict(self._asdict())
    return d
  
check.register_class(mmd_transition, include_seq = False)
