#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.log import logger
from ..system.check import check

from .btl_parser_node_error import btl_parser_node_error
from .btl_lexer_token import btl_lexer_token
from .btl_parser_node import btl_parser_node

class btl_parser_node_creator(object):

  _log = logger('parser_node_creator')
  
  def __init__(self, root_node_name = 'n_root'):
    check.check_string(root_node_name)
    
    self._root_node_name = root_node_name
    self._root_node = None
    self._nodes = {}

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
    
    if node_name in self._nodes:
      raise btl_parser_node_error(f'create: node already exists: "{node_name}"')

    node = btl_parser_node(node_name)
    self._nodes[node_name] = node

  def create_root(self):
    self.create(self._root_node_name)
    
  def set_token(self, node_name, token):
    check.check_string(node_name)
    check.check_btl_lexer_token(token)

    self.check_has_node(node_name)
    node = self._nodes[node_name]
    node.token = token.clone()

  def add_child(self, node_name, child_node_name):
    check.check_string(node_name)
    check.check_string(child_node_name)

    self.check_has_node(node_name)
    self.check_has_node(child_node_name)
    node = self._nodes[node_name]
    child_node = self.remove_node(child_node_name)
    node.add_child(child_node)

  def get_node(self, node_name):
    check.check_string(node_name)

    self.check_has_node(node_name)
    return self._nodes[node_name]

  def remove_node(self, node_name):
    check.check_string(node_name)

    self.check_has_node(node_name)
    result = self._nodes[node_name]
    del self._nodes[node_name]
    return result
  
  def get_root_node(self):
    return self.get_node(self._root_node_name)
    
#        node create n_key_value
#        node create n_key
#        node set_token n_key
#        node add n_key_value n_key
#      node create_root n_root
    

#    '''
#        node create n_key_value
#        node create n_key
#        node set_token n_key
#        node add n_key_value n_key
#      node create n_root
#        node create n_value
#        node set_token n_value
#        node add root n_key_value
#  '''
