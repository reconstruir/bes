#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.log import logger
from ..system.check import check

from .btl_parser_desc import btl_parser_desc
from .btl_parser_error import btl_parser_error
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

    first_token = self._tokens.find_backwards(token_index, 't_section_name_begin')
    first_index = first_token.index
    last_index = node.largest_index()
    last_token = self._tokens[last_index]
    
    if include_previous_line_break:
      new_line_before_token = self._tokens.find_backwards(first_index, 't_line_break')
      if new_line_before_token:
        first_token = new_line_before_token

    if include_next_line_break:
      new_line_after_token = self._tokens.find_forwards(last_index, 't_line_break')
      if new_line_after_token:
        last_token = new_line_after_token

    indeces_to_remove = [ i for i in reversed(range(first_token.index, last_token.index + 1)) ]
    for index_to_remove in indeces_to_remove:
      self._tokens.remove_by_index(index_to_remove)

    parent_node.remove_child(node)

    self._text = self._tokens.to_source_string()

  def add_comment_node(self, parent_node, comment_value):
    pass
    #token = btl_lexer_token('t_comment',
    #                          comment_value, position, type_hint, index')):

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
    self._do_parse()
    
check.register_class(btl_document, include_seq = False)
