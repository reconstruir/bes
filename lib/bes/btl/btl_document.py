#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from ..system.log import logger
from ..system.check import check
from ..property.cached_property import cached_property
from ..files.bf_file_ops import bf_file_ops
from ..files.bf_check import bf_check
from ..text.line_numbers import line_numbers

from .btl_comment_position import btl_comment_position
from .btl_document_error import btl_document_error
from .btl_parser_node import btl_parser_node
from .btl_parser_options import btl_parser_options
from .btl_lexer_token import btl_lexer_token

from abc import abstractmethod
from abc import ABCMeta

class btl_document(metaclass = ABCMeta):

  _log = logger('btl_document')
  
  def __init__(self, text, parser_options = None):
    check.check_string(text)
    check.check_btl_parser_options(parser_options, allow_none = True)

    lexer_class = self.lexer_class()
    parser_class = self.parser_class()
    check.check_class(lexer_class)
    check.check_class(parser_class)
    
    self._lexer = lexer_class()
    self._parser_options = parser_options or btl_parser_options()
    self._parser = parser_class(self._lexer)
    self.text = text
    self._root_node = None
    self._tokens = None
    self._do_parse()

  @classmethod
  @abstractmethod
  def lexer_class(clazz):
    raise NotImplementedError(f'lexer_class')

  @classmethod
  @abstractmethod
  def parser_class(clazz):
    raise NotImplementedError(f'parser_class')

#  @abstractmethod
#  def determine_insert_index(self, parent_node):
#    raise NotImplementedError(f'determine_insert_index')
  
  @property
  def root_node(self):
    return self._root_node

  @property
  def tokens(self):
    return self._tokens
  
  def to_source_string(self):
    return self._tokens.to_source_string()

  @property
  def text(self):
    return self._text

  @text.setter
  def text(self, text):
    self._text = text
    self._line_break_str = self._determine_line_break_str(self._text)

  @property
  def lexer(self):
    return self._lexer

  @property
  def parser(self):
    return self._parser
  
  @property
  def line_break_str(self):
    return self._line_break_str

  @classmethod
  def _determine_line_break_str(clazz, text):
    if '\r\n' in text:
      return '\r\n'
    elif '\n' in text:
      return '\n'
    else:
      return os.linesep
  
  def text_to_debug_str(self):
    return line_numbers.add_line_numbers(self.text)
  
  def _do_parse(self):
    self._root_node, self._tokens = self._parse_text(self._text)
    #self._log.log_d(f'=====:text:=====')
    #self._log.log_d(self._text)
    #self._log.log_d(f'================')
    source_string = self.to_source_string()
    #self._log.log_d(f'=====:source:=====')
    #self._log.log_d(source_string)
    #self._log.log_d(f'================')
    assert self.text == self.to_source_string()

  def _update_text(self):
    new_text = self.to_source_string()
    self.text = new_text
    self._log.log_d(f'_update_text: new_text:\n====\n{new_text}\n====', multi_line = True)
    
  def _parse_text(self, text):
    parser_result = self._parser.parse(text, options = self._parser_options)
    assert parser_result.tokens[-1].name == 't_done'
    parser_result.tokens.pop(-1)
    return parser_result.root_node, parser_result.tokens
    
  def reitre_node(self,
                  parent_node,
                  node,
                  starting_token_name,
                  include_previous_line_break,
                  include_next_line_break):
    token_index = node.token.index

    first_token = self._tokens.find_backwards_by_name(token_index, 't_section_name_begin')
    first_index = first_token.index
    last_index = node.largest_index()
    last_token = self._tokens[last_index]
    
    if include_previous_line_break:
      new_line_before_token = self._tokens.find_backwards_by_name(first_index, 't_line_break')
      if new_line_before_token:
        first_token = new_line_before_token

    if include_next_line_break:
      new_line_after_token = self._tokens.find_forwards_by_name(last_index, 't_line_break')
      if new_line_after_token:
        last_token = new_line_after_token

    indeces_to_remove = [ i for i in reversed(range(first_token.index, last_token.index + 1)) ]
    for index_to_remove in indeces_to_remove:
      self._tokens.remove_by_index(index_to_remove)

    parent_node.remove_child(node)

    self._update_text()

  @classmethod
  def _default_insert_index(clazz, parent_node, tokens):
    last_child = parent_node.find_last_node()
    if last_child and last_child.token:
      last_child_index = last_child.token.index
      clazz._log.log_d(f'_default_insert_index: last_child_index={last_child_index}')
      insert_index = last_child_index + 1
    elif parent_node.token:
      insert_index = parent_node.token.index + 1
    else:
      insert_index = 0
    return insert_index
    
  def add_node_from_text(self, parent_node, text, path, insert_index = None):
    'Parse text to a node tree and add that as a child of parent_node'
    check.check_btl_parser_node(parent_node)
    check.check_string(text)
    check.check_tuple(path, check.STRING_TYPES)
    check.check_int(insert_index, allow_none = True)

    assert insert_index != None
    
    self._log.log_d(f'add_node_from_text: insert_index={insert_index} text:\n====\n{text}\n====', multi_line = True)
    if insert_index == None:
      insert_index = self._default_insert_index(parent_node, self._tokens)
    self._log.log_d(f'add_node_from_text: insert_index={insert_index}')

    new_root_node, new_tokens = self._parse_text(text)
    self._log.log_d(f'add_node_from_text: new_root_node:\n====\n{str(new_root_node)}\n====', multi_line = True)
    new_node = new_root_node.find_child_by_path(path)
    if not new_node:
      path_flat = ', '.join(list(path))
      raise btl_document_error(f'Failed to find node with path: "{path_flat}"')

    self._log.log_d(f'add_node_from_text: self.root_node before:\n====\n{str(self.root_node)}\n====', multi_line = True)
    self._log.log_d(f'add_node_from_text: self.tokens before:\n====\n{self._tokens.to_debug_str()}\n====', multi_line = True)    
    self._log.log_d(f'add_node_from_text: new_node:\n====\n{str(new_node)}\n====', multi_line = True)
    self._log.log_d(f'add_node_from_text: new_tokens:\n====\n{new_tokens.to_debug_str()}\n====', multi_line = True)
    parent_node.add_child(new_node)
    self._log.log_d(f'add_node_from_text: self.root_node after:\n====\n{str(self.root_node)}\n====', multi_line = True)
    real_insert_index = self._tokens.insert_tokens(insert_index, new_tokens)
    self._log.log_d(f'add_node_from_text: real_insert_index={real_insert_index}')
    self._log.log_d(f'add_node_from_text: self.tokens after:\n====\n{self._tokens.to_debug_str()}\n====', multi_line = True)
    self._update_text()
    return self._tokens[real_insert_index].position.line

  @cached_property
  def comment_begin_char(self):
    vm = self._parser.lexer.desc.variables.to_variable_manager()
    variables = self._parser_options.variables
    return variables.get('v_comment_begin', vm.variables.get('v_comment_begin'))
    
  def add_comment(self, line, comment, position):
    check.check_int(line)
    check.check_string(comment)
    position = check.check_btl_comment_position(position)

    if position == position.NEW_LINE:
      text = f'{self.comment_begin_char}{comment}{self.line_break_str}'
      insert_index = self._tokens.first_line_to_index(line)
    elif position == position.END_OF_LINE:
      text = f' {self.comment_begin_char}{comment}'
      insert_index = self._tokens.last_line_to_index(line)
    elif position == position.START_OF_LINE:
      text = f'{self.comment_begin_char}{comment}'
      insert_index = self._tokens.first_line_to_index(line)

    new_node, tokens = self._parse_text(text)
    assert insert_index >= 0
    insert_index = self._tokens.insert_tokens(insert_index, tokens)
    self.text = self.to_source_string()
    return self._tokens[insert_index].position.line

  def add_line_break(self, line, count = 1):
    check.check_int(line)
    check.check_int(count)

    insert_index = self._tokens.last_line_to_index(line)
    self._log.log_d(f'add_line_break: line={line} insert_index={insert_index}')
    self._log.log_d(f'add_line_break: tokens before:\n====\n{self._tokens.to_debug_str()}\n====', multi_line = True)        
    tokens = count * [ btl_lexer_token(name = 't_line_break', value = self.line_break_str) ]
    self._tokens.insert_tokens(insert_index, tokens)
    
    self.text = self.to_source_string()
    self._log.log_d(f'add_line_break: tokens after:\n====\n{self._tokens.to_debug_str()}\n====', multi_line = True)
    insert_line = self._tokens[insert_index].position.line
    self._log.log_d(f'add_line_break: insert_line={insert_line}')
    return insert_line
    
  def save_file(self, filename, encoding = 'utf-8', backup = True, perm = None):
    check.check_string(encoding)
    check.check_bool(backup)
    
    new_text = self.to_source_string()
    if os.path.exists(filename):
      filename = bf_check.check_file(filename)
      old_text = bf_file_ops.read(filename, codec = codec)
      if old_text == new_text:
        return
      if backup:
        bf_file_ops.backup(filename)
      filename = bf_check.check_file(filename)
    else:
      filename = os.path.abspath(filename)
    bf_file_ops.save(filename, content = new_text, encoding = encoding, perm = None)
    
  @classmethod
  def load_file(clazz, filename, parser_options = None, codec = 'utf-8'):
    check.check_btl_parser_options(parser_options)
    
    if os.path.exists(filename):
      filename = bf_check.check_file(filename)
      text = bf_file_ops.read(filename, codec = codec)
    else:
      filename = os.path.abspath(filename)
      text = ''
      
    parser_options = parser_options or btl_parser_options()
    parser_options.source = filename
    return bc_ini_document(text, parser_options = parser_options)

  def insert_token(self, index, value):
    insert_index = self._tokens.insert_token(index, value)
    self.text = self.to_source_string()
    return insert_index

  def insert_tokens(self, index, values):
    insert_index = self._tokens.insert_tokens(index, values)
    self.text = self.to_source_string()
    return insert_index
  
check.register_class(btl_document, include_seq = False)
