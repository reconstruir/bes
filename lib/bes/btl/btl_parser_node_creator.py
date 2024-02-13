#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint

from collections import namedtuple

from ..system.log import log
from ..system.check import check

from .btl_parser_node_error import btl_parser_node_error
from .btl_lexer_token import btl_lexer_token
from .btl_parser_node import btl_parser_node

class btl_parser_node_creator(object):

  def __init__(self, log_tag, root_node_name = 'n_root'):
    check.check_string(log_tag)
    check.check_string(root_node_name)

    log.add_logging(self, tag = log_tag)
    
    self._root_node_name = root_node_name
    self._root_node = None
    self._nodes = {}

  def __len__(self):
    return len(self._nodes)

  def __str__(self):
    return pprint.pformat(self._nodes)
  
  def node_names(self):
    return sorted([ node_name for node_name in self._nodes.keys() ])
  
  def has_node(self, node_name):
    check.check_string(node_name)

    return node_name in self._nodes

  def check_has_node(self, node_name):
    check.check_string(node_name)

    if not self.has_node(node_name):
      raise btl_parser_node_error(f'node not found: "{node_name}"')
    
    return self._nodes[node_name]

  def check_does_not_have_node(self, node_name):
    check.check_string(node_name)

    if self.has_node(node_name):
      raise btl_parser_node_error(f'node already found: "{node_name}"')
    
  def create(self, node_name):
    check.check_string(node_name)

    self.log_d(f'node create {node_name}')
    if node_name in self._nodes:
      raise btl_parser_node_error(f'create: node already exists: "{node_name}"')
    node = btl_parser_node(node_name)
    self._nodes[node_name] = node

  def create_root(self):
    self.log_d(f'node create_root')
    self.create(self._root_node_name)
    
  def set_token(self, node_name, token):
    check.check_string(node_name)
    check.check_btl_lexer_token(token)

    self.log_d(f'node set_token {node_name} {token.to_debug_str()}')
    self.check_has_node(node_name)
    node = self._nodes[node_name]
    node.token = token.clone()

  def add_child(self, node_name, child_node_name):
    check.check_string(node_name)
    check.check_string(child_node_name)

    self.log_d(f'node add_child {node_name} {child_node_name}')
    self.check_has_node(node_name)
    self.check_has_node(child_node_name)
    node = self._nodes[node_name]
    child_node = self.remove_node(child_node_name)
    node.add_child(child_node)

  def add_child_if_it_exists(self, node_name, child_node_name):
    check.check_string(node_name)
    check.check_string(child_node_name)

    self.log_d(f'node add_child_if_it_exists {node_name} {child_node_name}')
    self.check_has_node(node_name)
    if not self.has_node(child_node_name):
      return
    self.add_child(node_name, child_node_name)
    
  def get_node(self, node_name):
    check.check_string(node_name)

    self.check_has_node(node_name)
    return self._nodes[node_name]

  def remove_node(self, node_name):
    check.check_string(node_name)

    self.log_d(f'node remove_node {node_name}')
    self.check_has_node(node_name)
    result = self._nodes[node_name]
    del self._nodes[node_name]
    return result
  
  def get_root_node(self):
    return self.get_node(self._root_node_name)

  def remove_root_node(self):
    self.log_d(f'node remove_root_node')
    return self.remove_node(self._root_node_name)
