#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..common.json_util import json_util
from ..fs.file_check import file_check
from ..fs.file_util import file_util
from ..system.check import check
from ..text.tree_text_parser import tree_text_parser
from ..version.semantic_version import semantic_version

from .btl_desc_char import btl_desc_char
from .btl_desc_char_map import btl_desc_char_map
from .btl_desc_error_list import btl_desc_error_list
from .btl_desc_header import btl_desc_header
from .btl_desc_mermaid import btl_desc_mermaid
from .btl_desc_state_list import btl_desc_state_list
from .btl_desc_token_list import btl_desc_token_list
from .btl_error import btl_error
from .btl_parsing import btl_parsing

class btl_desc(namedtuple('btl_desc', 'header, tokens, errors, char_map, states')):
  
  def __new__(clazz, header, tokens, errors, char_map, states):
    header = check.check_btl_desc_header(header)
    tokens = check.check_btl_desc_token_list(tokens)
    errors = check.check_btl_desc_error_list(errors)
    check.check_btl_desc_char_map(char_map)
    states = check.check_btl_desc_state_list(states)
    return clazz.__bases__[0].__new__(clazz, header, tokens, errors, char_map, states)

  def to_dict(self):
    return {
      'header': self.header.to_dict(),
      'tokens': self.tokens.as_sorted_list,
      'errors': self.errors.to_dict_list(),
      'char_map': self.char_map.to_dict(),
      'states': self.states.to_dict_list(),
    }

  def to_json(self):
    return json_util.to_json(self.to_dict(), indent = 2, sort_keys = False)

  def to_mermaid_diagram(self):
    return btl_desc_mermaid.desc_to_mermain_diagram(self)
  
  @classmethod
  def _parse_char_map(clazz, n, source):
    result = btl_desc_char_map()
    for child in n.children:
      name, chars = btl_parsing.parse_key_value(child, source)
      result.parse_and_add(name, chars)
    return result
  
  @classmethod
  def parse_text(clazz, text, source = '<unknown>'):
    check.check_string(text)
    check.check_string(source)

    root = tree_text_parser.parse(text, strip_comments = True, root_name = 'btl_desc')

    lexer_node = clazz._find_section(root, 'lexer', source)
    header = btl_desc_header.parse_node(lexer_node, source)
    #print(header)

    tokens_node = clazz._find_section(root, 'tokens', source)
    tokens = btl_desc_token_list.parse_node(tokens_node, source)
    #print(tokens)

    errors_node = clazz._find_section(root, 'errors', source)
    errors = btl_desc_error_list.parse_node(errors_node, source)
    #print(errors)

    states_node = clazz._find_section(root, 'states', source)
    states = btl_desc_state_list.parse_node(states_node, source, header.end_state)
    #print(states)

    chars_node = clazz._find_section(root, 'chars', source)
    char_map = clazz._parse_char_map(chars_node, source)
    #print(char_map)
    
    return btl_desc(header, tokens, errors, char_map, states)

  @classmethod
  def _find_section(clazz, root, name, source):
    assert root
    assert name
    assert source
    section_node = root.find_child_by_text(name)
    if not section_node:
      raise btl_error(f'Missing section "{section_node}" from "{source}"')
    return section_node
  
  @classmethod
  def parse_file(clazz, filename):
    filename = file_check.check_file(filename)
    text = file_util.read(filename, codec = 'utf-8')
    return clazz.parse_text(text, source = filename)

  def generate_code(self, buf, namespace, name):
    check.check_btl_code_gen_buffer(buf)
    check.check_string(namespace)
    check.check_string(name)

    buf.write_line(f'''
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.b_text_lexer.btl_lexer_base import btl_lexer_base
from bes.b_text_lexer.btl_lexer_state_base import btl_lexer_state_base
''')

    self.tokens.generate_code(buf, namespace, name)
    self.states.generate_code(buf, namespace, name, self.char_map)
    
    buf.write_lines(f'''
class {namespace}_{name}_lexer_base(text_lexer_base):

  def __init__(self, {name}, source = None):
    super().__init__(log_tag, source = source)

    self.token = {namespace}_{name}_lexer_token(self)
    self.char = text_lexer_char
    
''')

    with buf.indent_pusher(depth = 2) as _:
      buf.write_line('self._states = {')
      with buf.indent_pusher() as _42:
        for state in self.states:
          state_class_name = f'{namespace}_{name}_lexer_state_{state.name}'
          buf.write_line(f'\'{state.name}\': {state_class_name}(self),')
      buf.write_line('}')
  
check.register_class(btl_desc, include_seq = False)
