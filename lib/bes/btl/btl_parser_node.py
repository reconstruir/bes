#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

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

  def num_children(self):
    return len(self.children)

  def find_child_by_name(self, name):
    func = lambda node: node.name == name
    return self.find_child(func)

  def find_child_by_token(self, node_name, token_name, token_value):
    func = lambda node: node.name == node_name and node.token.name == token_name and node.token.value == token_value
    return self.find_child(func)
  
  def find_grandchild_by_token(self,
                               child_node_name,
                               grandchild_node_name,
                               token_name,
                               token_value):
    
    def _func(node):
      if node.name != child_node_name:
        return False
      grandchild_node = node.find_child_by_token(grandchild_node_name,
                                                 token_name,
                                                 token_value)
      return grandchild_node != None
    
    return self.find_child(_func, recurse = False)
  
  find_result = namedtuple('find_result', 'depth, child')

  def find_children(self, func, recurse = True):
    return self._find_children(func, 0, recurse)

  def find_child(self, func, recurse = True):
    found = self._find_children(func, 0, recurse)
    if not found:
      return None
    return found[0].child
  
  def _find_children(self, func, depth, recurse):
    result = []
    for child in self.children:
      if func(child):
        result.append(self.find_result(depth, child))
    if recurse:
      for child in self.children:
        result += child._find_children(func, depth + 1, recurse)
    return result

#  def ensure_path(self, path):
#    current_node = self
#    for part in path:
#      current_node = current_node.ensure_child(part)
#    return current_node

  def find_child_by_path(self, path, func):
    current_node = self
    for part in path:
      func2 = lambda n: func(n, part)
      current_node = current_node.find_child(func2, recurse = False)
      if current_node == None:
        return None
    return current_node

  def find_child_by_path_data(self, path):
    func = lambda n, part: n.data == part
    return self.find_child_by_path(path, func)

check.register_class(btl_parser_node, include_seq = False)

  
