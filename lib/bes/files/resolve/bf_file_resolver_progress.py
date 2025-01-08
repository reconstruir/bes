#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.common.json_util import json_util
from bes.common.tuple_util import tuple_util
from bes.common.string_util import string_util

from .bf_file_resolver_progress_state import bf_file_resolver_progress_state
from .bf_file_resolver_error import bf_file_resolver_error

class bf_file_resolver_progress(namedtuple('bf_file_resolver_progress', 'state, index, total')):

  def __new__(clazz, state, index, total):
    state = check.check_bf_file_resolver_progress_state(state)
    check.check_int(index, allow_none = True)
    check.check_int(total, allow_none = True)

    if state == bf_file_resolver_progress_state.SCANNING:
      if index != None:
        raise bf_file_resolver_error(f'if state is "SCANNING" index should be None: "{index}"')
      if total != None:
        raise bf_file_resolver_error(f'if state is "SCANNING" total should be None: "{total}"')
    elif state == bf_file_resolver_progress_state.FINDING:
      if index == None:
        raise bf_file_resolver_error(f'if state is "FINDING" index should not be None')
      if total == None:
        raise bf_file_resolver_error(f'if state is "FINDING" total should not be None')
    
    return clazz.__bases__[0].__new__(clazz, state, index, total)

  def to_dict(self):
    return dict(self._asdict())
  
  def to_json(self):
    return json_util.to_json(self.to_dict(), indent = 2, sort_keys = True)
  
  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)

  @property
  def rounded_percent_done(self):
    return round(self.percent_done)

  @property
  def percent_done(self):
    return (self.index / self.total) * 100.0
  
check.register_class(bf_file_resolver_progress, include_seq = False)
