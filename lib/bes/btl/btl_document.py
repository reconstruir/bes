#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from ..system.log import logger
from ..system.check import check
from ..property.cached_property import cached_property
from ..files.bf_file_ops import bf_file_ops
from ..files.bf_check import bf_check

from .btl_comment_position import btl_comment_position
from .btl_document_error import btl_document_error
from .btl_parser_node import btl_parser_node
from .btl_parser_options import btl_parser_options

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
    
    lexer = lexer_class()
    self._parser_options = parser_options or btl_parser_options()
    self._parser = parser_class(lexer)
    self._text = text
    self._root_node = None
    self._tokens = None
    self._do_parse()

  @classmethod
  @abstractmethod
  def lexer_class(clazz):
    raise NotImplementedError(f'not implemented: "lexer_class"')

  @classmethod
  @abstractmethod
  def parser_class(clazz):
    raise NotImplementedError(f'not implemented: "parser_class"')
  
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
  
  def _do_parse(self):
    self._root_node, self._tokens = self._parse_text(self._text, include_done = True)
    #self._log.log_d(f'=====:text:=====')
    #self._log.log_d(self._text)
    #self._log.log_d(f'================')
    source_string = self.to_source_string()
    #self._log.log_d(f'=====:source:=====')
    #self._log.log_d(source_string)
    #self._log.log_d(f'================')
    assert self._text == self.to_source_string()

  def _parse_text(self, text, include_done = False):
    new_node, new_tokens = self._parser.parse(text, options = self._parser_options)
    if not include_done:
      assert len(new_tokens) > 0
      new_tokens.remove_by_index(-1)
    return new_node, new_tokens
    
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

    self._text = self._tokens.to_source_string()

  def add_node_from_text(self, parent_node, text, path):
    'Parse text to a node tree and add that as a child of parent_node'
    check.check_btl_parser_node(parent_node)
    check.check_string(text)
    check.check_tuple(path, check.STRING_TYPES)

    self._log.log_d(f'add_node_from_text: text:\n====\n{text}\n====', multi_line = True)
    last_child = parent_node.find_last_node()
    last_child_index = last_child.token.index
    self._log.log_d(f'add_node_from_text: last_child_index={last_child_index}')
    new_root_node, new_tokens = self._parse_text(text)
    self._log.log_d(f'add_node_from_text: new_root_node:\n====\n{str(new_root_node)}\n====', multi_line = True)
    self._log.log_d(f'add_node_from_text: new_tokens:\n====\n{new_tokens.to_debug_str()}\n====', multi_line = True)

    new_node = new_root_node.find_child_by_path(path)
    if not new_node:
      path_flat = ', '.join(list(path))
      raise btl_document_error(f'Failed to find node with path: "{path_flat}"')
      
    self._log.log_d(f'add_node_from_text: new_node:\n====\n{str(new_node)}\n====', multi_line = True)
    parent_node.add_child(new_node)
    self._log.log_d(f'add_node_from_text: root_node:\n====\n{str(self.root_node)}\n====', multi_line = True)
    insert_index = last_child_index + 1
    self._log.log_d(f'add_node_from_text: insert_index={insert_index}')
    self._tokens.insert_values(insert_index, new_tokens)
    self._log.log_d(f'add_node_from_text: self._tokens:\n====\n{self._tokens.to_debug_str()}\n====', multi_line = True)
    new_text = self.to_source_string()
    self._log.log_d(f'add_node_from_text: new_text:\n====\n{new_text}\n====', multi_line = True)
    self._text = new_text
    # FIXME: reparse the document to fix the indeces.
    # obviously this is inefficient.  better would be to renumber
    self._do_parse()
    return new_node

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
      text = f'{self.comment_begin_char}{comment}{os.linesep}'
      insert_index = self._tokens.first_line_to_index(line)
    elif position == position.END_OF_LINE:
      text = f' {self.comment_begin_char}{comment}'
      insert_index = self._tokens.last_line_to_index(line)
    elif position == position.START_OF_LINE:
      text = f'{self.comment_begin_char}{comment}'
      insert_index = self._tokens.first_line_to_index(line)

    new_node, tokens = self._parse_text(text)
    assert insert_index >= 0
    self._tokens.insert_values(insert_index, tokens)
    self._text = self.to_source_string()
    # FIXME: reparse the document to fix the indeces.
    # obviously this is inefficient.  better would be to renumber
    self._do_parse()

  def save_file(self, filename, encoding = 'utf-8', backup = True, perm = None):
    check.check_string(encoding)
    check.check_bool(backup)
    
    new_text = self.to_source_string()
    if path.exists(filename):
      filename = bf_check.check_file(filename)
      old_text = bf_file_ops.read(filename, codec = codec)
      if old_text == new_text:
        return
      if backup:
        bf_file_ops.backup(filename)
      filename = bf_check.check_file(filename)
    else:
      filename = path.abspath(filename)
    bf_file_ops.save(filename, content = new_text, encoding = encoding, perm = None)
    
  @classmethod
  def load_file(clazz, filename, parser_options = None, codec = 'utf-8'):
    check.check_btl_parser_options(parser_options)
    
    if path.exists(filename):
      filename = bf_check.check_file(filename)
      text = bf_file_ops.read(filename, codec = codec)
    else:
      filename = path.abspath(filename)
      text = ''
      
    parser_options = parser_options or btl_parser_options()
    parser_options.source = filename
    return bc_ini_document(text, parser_options = parser_options)
    
check.register_class(btl_document, include_seq = False)
