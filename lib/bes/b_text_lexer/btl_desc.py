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
from .btl_desc_state_list import btl_desc_state_list
from .btl_error import btl_error
from .btl_parsing import btl_parsing

class btl_desc(namedtuple('btl_desc', 'header, tokens, errors, char_map, states')):
  
  def __new__(clazz, header, tokens, errors, char_map, states):
    header = check.check_btl_desc_header(header)
    check.check_string_seq(tokens)
    errors = check.check_btl_desc_error_list(errors)
    check.check_btl_desc_char_map(char_map)
    states = check.check_btl_desc_state_list(states)
    return clazz.__bases__[0].__new__(clazz, header, tokens, errors, char_map, states)

  def to_dict(self):
    return {
      'header': self.header.to_dict(),
      'tokens': sorted([ token for token in self.tokens ]),
      'errors': self.errors.to_dict_list(),
      'char_map': self.char_map.to_dict(),
      'states': self.states.to_dict_list(),
    }

  def to_json(self):
    return json_util.to_json(self.to_dict(), indent = 2, sort_keys = False)
  
  @classmethod
  def _parse_tokens(clazz, n, source):
    result = set()
    for child in n.children:
      token_name = child.data.text.strip()
      if token_name in result:
        raise btl_error(f'Duplicate token "{token_name}" at {source}:{child.data.line_number}')
      result.add(token_name)
    return result

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
    tokens = clazz._parse_tokens(tokens_node, source)
    #print(tokens)

    errors_node = clazz._find_section(root, 'errors', source)
    errors = btl_desc_error_list.parse_node(errors_node, source)
    #print(errors)

    states_node = clazz._find_section(root, 'states', source)
    states = btl_desc_state_list.parse_node(states_node, source)
    #print(states)

    chars_node = clazz._find_section(root, 'chars', source)
    char_map = clazz._parse_char_map(chars_node, source)
    #print(char_map)
    
    return btl_desc(header, tokens, errors, char_map, states)

  @classmethod
  def _find_section(clazz, root, name, source):
    section_node = root.find_child_by_text(name)
    if not section_node:
      raise btl_error(f'Missing section "{section_node}" from "{source}"')
    return section_node
  
  @classmethod
  def parse_file(clazz, filename):
    filename = file_check.check_file(filename)
    text = file_util.read(filename, codec = 'utf-8')
    return clazz.parse_text(text, source = filename)
    
check.register_class(btl_desc)
