#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from collections import OrderedDict

from ..system.check import check
from ..version.semantic_version import semantic_version

from .btl_error import btl_error
from .btl_parsing import btl_parsing
from .btl_desc_state_transition_list import btl_desc_state_transition_list

class btl_desc_state(namedtuple('btl_desc_state', 'name, transitions, is_end_state')):
  
  def __new__(clazz, name, transitions, is_end_state):
    check.check_string(name)
    check.check_bool(is_end_state)
    
    transitions = check.check_btl_desc_state_transition_list(transitions)
    return clazz.__bases__[0].__new__(clazz, name, transitions, is_end_state)

  def to_dict(self):
    return {
      'name': self.name,
      'transitions': self.transitions.to_dict_list(),
      'is_end_state': self.is_end_state,
    }
  
  @classmethod
  def parse_node(clazz, n, end_state, source = '<unknown>'):
    check.check_node(n)
    check.check_string(end_state)

    name = n.data.text.strip()
    transitions = btl_desc_state_transition_list.parse_node(n, source = source)
    return btl_desc_state(name, transitions, name == end_state)

check.register_class(btl_desc_state, include_seq = False)
