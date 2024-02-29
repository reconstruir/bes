#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..common.json_util import json_util
from ..common.variable_manager import variable_manager
from ..fs.file_check import file_check
from ..fs.file_util import file_util
from ..system.check import check
from ..text.tree_text_parser import tree_text_parser
from ..version.semantic_version import semantic_version

from .btl_code_gen_buffer import btl_code_gen_buffer
from .btl_desc_text_node import btl_desc_text_node
from .btl_error import btl_error
from .btl_lexer_desc_char import btl_lexer_desc_char
from .btl_lexer_desc_char_map import btl_lexer_desc_char_map
from .btl_lexer_desc_error_list import btl_lexer_desc_error_list
from .btl_lexer_desc_function_list import btl_lexer_desc_function_list
from .btl_lexer_desc_header import btl_lexer_desc_header
from .btl_lexer_desc_mermaid import btl_lexer_desc_mermaid
from .btl_lexer_desc_state_list import btl_lexer_desc_state_list
from .btl_lexer_desc_token_list import btl_lexer_desc_token_list
from .btl_lexer_desc_variable_list import btl_lexer_desc_variable_list

class btl_lexer_desc(namedtuple('btl_lexer_desc', 'header, tokens, errors, variables, functions, char_map, states, source_text')):
  
  def __new__(clazz, header, tokens, errors, variables, functions, char_map, states, source_text = None):
    header = check.check_btl_lexer_desc_header(header)
    tokens = check.check_btl_lexer_desc_token_list(tokens)
    errors = check.check_btl_lexer_desc_error_list(errors)
    variables = check.check_btl_lexer_desc_variable_list(variables)
    functions = check.check_btl_lexer_desc_function_list(functions)
    check.check_btl_lexer_desc_char_map(char_map)
    states = check.check_btl_lexer_desc_state_list(states)
    check.check_string(source_text, allow_none = True)

    source_text = source_text or ''
    return clazz.__bases__[0].__new__(clazz,
                                      header,
                                      tokens,
                                      errors,
                                      variables,
                                      functions,
                                      char_map,
                                      states,
                                      source_text)

  def to_dict(self):
    return {
      'header': self.header.to_dict(),
      'tokens': self.tokens.to_dict_list(),
      'errors': self.errors.to_dict_list(),
      'variables': self.variables.to_dict_list(),
      'functions': self.functions.to_dict_list(),
      'char_map': self.char_map.to_dict(),
      'states': self.states.to_dict_list(),
    }

  def to_json(self):
    return json_util.to_json(self.to_dict(), indent = 2, sort_keys = False)

  def to_mermaid_diagram(self):
    return btl_lexer_desc_mermaid.desc_to_mermain_diagram(self)
  
  @classmethod
  def _parse_char_map(clazz, n, variable_manager, source):
    result = btl_lexer_desc_char_map(variable_manager)
    if n:
      for child in n.children:
        name, chars = child.parse_key_value(source)
        result.parse_and_add(name, chars)
    return result
  
  @classmethod
  def parse_text(clazz, text, source = '<unknown>'):
    check.check_string(text)
    check.check_string(source)

    root = tree_text_parser.parse(text,
                                  strip_comments = True,
                                  root_name = 'btl_lexer_desc',
                                  node_class = btl_desc_text_node)

    lexer_node = root.find_tree_section('lexer', source)
    header = btl_lexer_desc_header.parse_node(lexer_node, source)
    #print(header)

    tokens_node = root.find_tree_section('tokens', source, raise_error = False)
    tokens = btl_lexer_desc_token_list.parse_node(tokens_node, source)
    #print(tokens)

    errors_node = root.find_tree_section('errors', source, raise_error = False)
    errors = btl_lexer_desc_error_list.parse_node(errors_node, source)
    #print(errors)

    states_node = root.find_tree_section('states', source, raise_error = False)
    states = btl_lexer_desc_state_list.parse_node(states_node, source)
    #print(states)

    variables_node = root.find_tree_section('variables', source, raise_error = False)
    variables = btl_lexer_desc_variable_list.parse_node(variables_node, source)
    #print(variables)

    functions_node = root.find_tree_section('functions', source, raise_error = False)
    functions = btl_lexer_desc_function_list.parse_node(functions_node, source)
    #print(functions)
    
    chars_node = root.find_tree_section('chars', source, raise_error = False)
    char_map = clazz._parse_char_map(chars_node, variables.to_variable_manager(), source)
    #print(char_map)

    return btl_lexer_desc(header,
                          tokens,
                          errors,
                          variables,
                          functions,
                          char_map,
                          states,
                          source_text = text)

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

from bes.btl.btl_function_base import btl_function_base
from bes.btl.btl_lexer_base import btl_lexer_base
from bes.btl.btl_lexer_runtime_error import btl_lexer_runtime_error
from bes.btl.btl_lexer_state_base import btl_lexer_state_base
from bes.btl.btl_lexer_token import btl_lexer_token
from bes.system.check import check
''')

    buf.write_line(f'class {namespace}_{name}(btl_lexer_base):')
    buf.write_linesep()
    with buf.indent_pusher(depth = 1) as _:
      self.tokens.generate_code(buf)
      buf.write_linesep()
      self.errors.generate_code(buf)
      buf.write_linesep()
      self.states.generate_code(buf, self.errors, self.char_map)

    buf.write_lines(f'''
  def __init__(self, desc_source = None):
    log_tag = f'{namespace}_{name}'
    desc_text = self._DESC_TEXT
    token = self._token
''')
    with buf.indent_pusher(depth = 2) as _:
      buf.write_line('states = {')
      with buf.indent_pusher() as _42:
        for state in self.states:
          state_class_name = f'_state_{state.name}'
          buf.write_line(f'\'{state.name}\': self.{state_class_name}(self, log_tag),')
      buf.write_line('}')
      buf.write_lines(f'super().__init__(log_tag, desc_text, token, states, desc_source = desc_source)')

    with buf.indent_pusher(depth = 1) as _:
      desc_text = self.source_text or ''
      buf.write_line(f'_DESC_TEXT = """')
    buf.write_line(f'{self.source_text}')
    buf.write_line(f'"""')
    buf.write_line(f'check.register_class({namespace}_{name}, include_seq = False)')
      
  def write_code(self, output_filename, namespace, name, indent_width = 2):
    check.check_string(output_filename)
    check.check_string(namespace)
    check.check_string(name)
    check.check_int(indent_width)

    buf = btl_code_gen_buffer(indent_width = indent_width)
    self.generate_code(buf, namespace, name)
    file_util.save(output_filename, content = buf.get_value())

  def make_variable_manager(self, variables):
    check.check_dict(variables, check.STRING_TYPES, check.STRING_TYPES)

    combined = self.variables.to_dict()
    combined.update(variables)
    return variable_manager(combined)
    
check.register_class(btl_lexer_desc, include_seq = False)
