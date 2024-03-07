#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from .btl_parser_node import btl_parser_node
from .btl_lexer_token_list import btl_lexer_token_list

class btl_parser_result(object):

  def __init__(self, root_node, tokens):
    check.check_btl_parser_node(root_node)
    check.check_btl_lexer_token_list(tokens)

    self._root_node = root_node
    self._tokens = tokens

  @property
  def root_node(self):
    return self._root_node

  @property
  def tokens(self):
    return self._tokens
  
check.register_class(btl_parser_result, include_seq = False)
