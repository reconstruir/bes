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

  def generate_code(self, buf, char_map):
    check.check_btl_code_gen_buffer(buf)
    check.check_btl_desc_char_map(char_map)

    buf.write_lines(f'''
class _state_{self.name}(btl_lexer_state_base):
  def __init__(self, lexer, log_tag):
    name = '{self.name}'
    super().__init__(lexer, name, log_tag)

  def handle_char(self, c):
    self.log_handle_char(c)

    new_state = None
    tokens = []

''')

    with buf.indent_pusher(depth = 2) as _:
      self.transitions.generate_code(buf, char_map)
      buf.write_lines(f'''
self.lexer.change_state(new_state, c)
return tokens
''')
  
check.register_class(btl_desc_state, include_seq = False)
