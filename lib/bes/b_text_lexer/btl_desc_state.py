#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from collections import OrderedDict

from ..system.check import check
from ..version.semantic_version import semantic_version

from .btl_error import btl_error
from .btl_parsing import btl_parsing
from .btl_desc_state_transition_list import btl_desc_state_transition_list

class btl_desc_state(namedtuple('btl_desc_state', 'name, transitions')):
  
  def __new__(clazz, name, transitions):
    check.check_string(name)
    transitions = check.check_btl_desc_state_transition_list(transitions)
    return clazz.__bases__[0].__new__(clazz, name, transitions)

  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n)

    name = n.data.text.strip()
    transitions = btl_desc_state_transition_list.parse_node(n, source = source)
    return btl_desc_state(name, transitions)

check.register_class(btl_desc_state, include_seq = False)
