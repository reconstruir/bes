#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..common.string_util import string_util
from ..common.tuple_util import tuple_util
from ..common.json_util import json_util
from ..system.check import check

from .mmd_transition_list import mmd_transition_list

class mmd_document(namedtuple('mmd_document', 'states, tokens, transitions')):

  def __new__(clazz, states, tokens, transitions):
    check.check_string_seq(states)
    check.check_string_seq(tokens)
    check.check_mmd_transition_list(transitions)

    return clazz.__bases__[0].__new__(clazz, states, tokens, transitions)

  def to_dict(self):
    d = dict(self._asdict())
    d['transitions'] = self.transitions.to_dict_list()
    return d

  def to_json(self):
    return json_util.to_json(self.to_dict(), indent = 2, sort_keys = False)
  
check.register_class(mmd_document, include_seq = False)
