#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import io
import os

from ..system.check import check

from .btl_parser_node_error import btl_parser_node_error
from .btl_lexer_token import btl_lexer_token

class btl_parser_node(object):

  def __init__(self, name, token = None):
    check.check_string(name)
    check.check_btl_lexer_token(token, allow_none = True)

    self._name = name
    self._token = token
    self._children = []

  def __str__(self):
    return self.to_string(0)

  def __repr__(self):
    return self.to_string(0)
  
  def to_string(self, depth = 0, indent = 2, rstrip = True):
    buf = io.StringIO()
    buf.write(' ' * depth)
    token_str = str(self.token) if self.token else ''
    data_str = f'{self._name};{token_str}'
    buf.write(data_str)
    buf.write(os.linesep)
    for child in self.children:
      buf.write(child.to_string(depth + indent, rstrip = False))
    result = buf.getvalue()
    if rstrip:
      result = result.rstrip()
    return result
  
  @property
  def name(self):
    return self._name

  @property
  def token(self):
    return self._token

  @property
  def children(self):
    return self._children
  
  @token.setter
  def token(self, token):
    self._token = token

  def add_child(self, child):
    check.check_btl_parser_node(child)

    self._children.append(child)

check.register_class(btl_parser_node, include_seq = False)

  
