#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from ..system.log import logger
from ..system.check import check
from ..property.cached_property import cached_property

from .btl_comment_position import btl_comment_position
from .btl_parser_node import btl_parser_node
from .btl_parser_options import btl_parser_options

class btl_document(object):

  _log = logger('btl_document')
  
  def __init__(self, parser, text, parser_options = None):
    check.check_btl_parser(parser)
    check.check_string(text)
    check.check_btl_parser_options(parser_options, allow_none = True)

    self._parser_options = parser_options or btl_parser_options()
    self._parser = parser
    self._text = text
    self._root_node = None
    self._tokens = None
    self._do_parse()

  @property
  def root_node(self):
    return self._root_node

  @property
  def tokens(self):
    return self._tokens
  
  def to_source_string(self):
    return self._tokens.to_source_string()
    
  def _do_parse(self):
    self._root_node, self._tokens = self._parse_text(self._text)
    #self._log.log_d(f'=====:text:=====')
    #self._log.log_d(self._text)
    #self._log.log_d(f'================')
    source_string = self.to_source_string()
    #self._log.log_d(f'=====:source:=====')
    #self._log.log_d(source_string)
    #self._log.log_d(f'================')
    assert self._text == self.to_source_string()

  def _parse_text(self, text):
    return self._parser.parse(text, options = self._parser_options)
    
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

  def add_node_from_text(self, parent_node, text):
    'Parse text to a node tree and add that as a child of parent_node'
    check.check_btl_parser_node(parent_node)
    check.check_string(text)

    last_child = parent_node.find_last_node()
    last_child_index = last_child.token.index
    new_node, tokens = self._parse_text(text)
    parent_node.add_child(new_node)
    self._tokens.insert_values(last_child_index + 1, tokens)
    self._text = self.to_source_string()
    # FIXME: reparse the document to fix the indeces.
    # obviously this is inefficient.  better would be to renumber
    self._do_parse()

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
      new_node, tokens = self._parse_text(text)
      # remove the t_done token
      tokens.remove_by_index(-1)
      first_line_index = self._tokens.first_line_to_index(line)
      assert first_line_index >= 0
      self._tokens.insert_values(first_line_index - 0, tokens)
    elif position == position.END_OF_LINE:
      text = f' {self.comment_begin_char}{comment}'
      new_node, tokens = self._parse_text(text)
      # remove the t_done token
      tokens.remove_by_index(-1)
      last_line_index = self._tokens.last_line_to_index(line)
      assert last_line_index >= 0
      self._tokens.insert_values(last_line_index - 0, tokens)
      pass
    elif position == position.START_OF_LINE:
      pass
    
    self._text = self.to_source_string()
    # FIXME: reparse the document to fix the indeces.
    # obviously this is inefficient.  better would be to renumber
    self._do_parse()

check.register_class(btl_document, include_seq = False)
