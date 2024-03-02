#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path

from bes.system.check import check

from bes.btl.btl_document import btl_document
from bes.btl.btl_parser_options import btl_parser_options

from .bc_ini_lexer import bc_ini_lexer
from .bc_ini_parser import bc_ini_parser
from .bc_ini_error import bc_ini_error

class bc_ini_document(btl_document):

  @classmethod
  #@abstractmethod
  def lexer_class(clazz):
    return bc_ini_lexer

  @classmethod
  #@abstractmethod
  def parser_class(clazz):
    return bc_ini_parser
    
      
  def get_value(self, key):
    check.check_string(key)
    
    kv_node = self._find_global_key_value_node(key, raise_error = True)
    return kv_node.children[1].token.value
    
  def set_value(self, key, value):
    check.check_string(key)
    check.check_string(value)

    kv_node = self._find_global_key_value_node(key, raise_error = True)
    self._key_value_node_modify_value(kv_node, value)
    
  def remove_value(self, key):
    check.check_string(key)

  def has_section(self, section_name):
    check.check_string(section_name)

    section_node = self.find_section_node(section_name, raise_error = False)
    return section_node != None
    
  def get_section_value(self, section_name, key):
    check.check_string(section_name)
    check.check_string(key)

    kv_node = self._find_section_key_value_node(section_name, key, raise_error = True)
    return kv_node.children[1].token.value
    
  def set_section_value(self, section_name, key, value):
    check.check_string(section_name)
    check.check_string(key)
    check.check_string(value)

    kv_node = self._find_section_key_value_node(section_name, key, raise_error = False)
    if kv_node:
      self._key_value_node_modify_value(kv_node, value)
    else:
      section_node = self.find_section_node(section_name, raise_error = False)
      if not section_node:
        section_node = self.add_section(section_name)
      kv_node = self.add_node_from_text(section_node.find_last_node(), f'\n{key}={value}')
    
  def add_section(self, section_name):
    check.check_string(section_name)

    sections_node = self.root_node.find_child_by_name('n_sections')
    return self.add_node_from_text(sections_node, f'\n\n[{section_name}]\n')
    
  def remove_section_value(self, section_name, key):
    check.check_string(section_name)
    check.check_string(key)
    
  def remove_section(self, section_name):
    check.check_string(section_name)

    sections_node = self.root_node.find_child_by_name('n_sections')
    section_node =  self.find_section_node(section_name, raise_error = True)
    self.reitre_node(sections_node, section_node, 't_section_name_begin', True, True)

  def find_global_section_node(self):
    global_section_node = self.root_node.find_child_by_name('n_global_section')
    if not global_section_node:
      raise bc_ini_error(f'missing node: "n_global_section"')
    return global_section_node

  def find_sections_node(self):
    sections_node = self.root_node.find_child_by_name('n_sections')
    if not sections_node:
      raise bc_ini_error(f'missing node: "n_sections"')
    return sections_node
  
  def find_section_node(self, section_name, raise_error = True):
    sections_node = self.find_sections_node()
    section_node = sections_node.find_child_by_token('n_section',
                                                     't_section_name',
                                                     section_name)
    if not section_node and raise_error:
      raise bc_ini_error(f'section not found in document: "{section_name}"')
    return section_node

  def _find_section_key_value_node(self, section_name, key, raise_error = True):
    section_node =  self.find_section_node(section_name, raise_error = True)
    key_value_node = section_node.find_grandchild_by_token('n_key_value',
                                                           'n_key',
                                                           't_key',
                                                           key)
    if not key_value_node and raise_error:
      raise bc_ini_error(f'key value not found in section "{section_name}": "{key}"')
    return key_value_node

  def _find_global_key_value_node(self, key, raise_error = True):
    global_section_node = self.root_node.find_child_by_name('n_global_section')
    if not global_section_node:
      raise bc_ini_error(f'missing node: "n_global_section"')
    key_value_node = global_section_node.find_grandchild_by_token('n_key_value',
                                                                  'n_key',
                                                                  't_key',
                                                                  key)
    if not key_value_node and raise_error:
      raise bc_ini_error(f'key value not found: "{key}"')
    return key_value_node

  def _key_value_node_modify_value(self, key_value_node, new_value):
    token = key_value_node.children[1].token
    token.replace_value(new_value)

check.register_class(bc_ini_document, include_seq = False)
