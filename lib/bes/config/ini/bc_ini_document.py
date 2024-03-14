#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path

from bes.system.check import check

from bes.btl.btl_document_base import btl_document_base
from bes.btl.btl_parser_options import btl_parser_options

from .bc_ini_lexer import bc_ini_lexer
from .bc_ini_parser import bc_ini_parser
from .bc_ini_error import bc_ini_error

class bc_ini_document(btl_document_base):

  @classmethod
  #@abstractmethod
  def lexer_class(clazz):
    return bc_ini_lexer

  @classmethod
  #@abstractmethod
  def parser_class(clazz):
    return bc_ini_parser

  @classmethod
  #@abstractmethod
  def exception_class(clazz):
    return bc_ini_error

  #@abstractmethod
  def determine_insert_index(self, parent_node, child_node, new_tokens):
    self._log.log_d(f'determine_insert_index: parent_node="{parent_node}" new_tokens="{new_tokens}"')
    return self._default_insert_index(parent_node, self._tokens)
  
  def get_value(self, key):
    check.check_string(key)
    
    kv_node = self._find_global_key_value_node(key, raise_error = True)
    return kv_node.children[1].token.value
    
  def set_value(self, key, value):
    check.check_string(key)
    check.check_string(value)

    self._log.log_d(f'set_value: key="{key}" value="{value}"')
    self._log.log_d(f'set_value: tokens before:\n{self._tokens.to_debug_str()}', multi_line = True)
    self._log.log_d(f'set_value: root_node before:\n{str(self._root_node)}', multi_line = True)
    kv_node = self._find_global_key_value_node(key, raise_error = True)
    self._key_value_node_modify_value(kv_node, value)
    self._update_text()
    self._log.log_d(f'set_value: tokens after:\n{self._tokens.to_debug_str()}', multi_line = True)
    self._log.log_d(f'set_value: root_node after:\n{str(self._root_node)}', multi_line = True)

  def add_value(self, key, value):
    check.check_string(key)
    check.check_string(value)

    global_section_node = self._find_global_section_node()
    text = f'{os.linesep}{key}={value}'
    result = self.add_node_from_text(global_section_node,
                                     text,
                                     ( 'n_global_section', 'n_key_value' ))
    return result

  def remove_value(self, key):
    check.check_string(key)
    assert False

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
      self.add_node_from_text(section_node,
                              f'{self.line_break_str}{key}={value}',
                              ( 'n_sections', 'n_key_value', ))
    self._update_text()

  def _determine_section_value_insert_index(self, section_node):
    last_index = section_node.find_last_node().token.index
    self._log.log_d(f'_determine_section_value_insert_index: last_index={last_index}')
    if section_node.children:
      #print(f'poto={poto} section={section_node.name}')
      #print(f'-----')
      #for t in self._tokens[last_index + 1:]:
      #  print(t.to_debug_str())
      #print(f'-----')
#      poto = self._tokens.find_index_forwards_by_name(last_index + 1, 't_line_break', raise_error = False)
      #def find_index_forwards_by_name(self, index, token_name, negate = False, raise_error = False, error_message = None):
      #skip_index_forwards_by_name(self, index, token_name, num, negate = False, raise_error = False, error_message = None):
      poto = self._tokens.skip_index_forwards_by_name(last_index + 1, 't_line_break', -1, raise_error = False)
      self._log.log_d(f'_determine_section_value_insert_index: 1 poto={poto}')
      insert_index = poto
    else:
      section_end_token = self._tokens.find_forwards_by_name(last_index, 't_section_name_end')
      insert_index = section_end_token.index + 1
      poto = self._tokens.skip_index_forwards_by_name(insert_index, 't_line_break', -1, raise_error = False)
      self._log.log_d(f'_determine_section_value_insert_index: 2 poto={poto}')
      insert_index = poto + 1
      
    self._log.log_d(f'_determine_section_value_insert_index: insert_index={insert_index}')
    self._log.log_d(f'_determine_section_value_insert_index: tokens={self._tokens.to_debug_str()}', multi_line = True)
    return insert_index
      
  def add_section_value(self, section_name, key, value):
    check.check_string(section_name)
    check.check_string(key)
    check.check_string(value)

    section_node = self.find_section_node(section_name, raise_error = True)
    text = f'{os.linesep}{key}={value}'
#    insert_index = self._determine_section_value_insert_index(section_node)
    return self.add_node_from_text(section_node,
                                   text,
                                   ( 'n_global_section', 'n_key_value'))

  def _determine_section_insert_index(self, section_node):
    last_node = section_node.find_last_node()
    self._log.log_e(f'_determine_section_insert_index: last_node={last_node}')
    if not last_node.token:
      return -1 #section_node.token.index
    self._log.log_e(f'_determine_section_insert_index: last_node_token={last_node.token}')
    last_index = last_node.token.index
    self._log.log_d(f'_determine_section_insert_index: last_index={last_index}')
    if section_node.children:
      #print(f'poto={poto} section={section_node.name}')
      #print(f'-----')
      #for t in self._tokens[last_index + 1:]:
      #  print(t.to_debug_str())
      #print(f'-----')
#      poto = self._tokens.find_index_forwards_by_name(last_index + 1, 't_line_break', raise_error = False)
      #def find_index_forwards_by_name(self, index, token_name, negate = False, raise_error = False, error_message = None):
      #skip_index_forwards_by_name(self, index, token_name, num, negate = False, raise_error = False, error_message = None):
      poto = self._tokens.skip_index_forwards_by_name(last_index + 1, 't_line_break', -1, raise_error = False)
      self._log.log_d(f'_determine_section_insert_index: 1 poto={poto}')
      insert_index = poto
    else:
      section_end_token = self._tokens.find_forwards_by_name(last_index, 't_section_name_end')
      insert_index = section_end_token.index + 1
      poto = self._tokens.skip_index_forwards_by_name(insert_index, 't_line_break', -1, raise_error = False)
      self._log.log_d(f'_determine_section_insert_index: 2 poto={poto}')
      insert_index = poto + 1
      
    self._log.log_d(f'_determine_section_insert_index: insert_index={insert_index}')
    self._log.log_d(f'_determine_section_insert_index: tokens={self._tokens.to_debug_str()}', multi_line = True)
    return insert_index
  
  def add_section(self, section_name, line_break_before = True, line_break_after = True):
    check.check_string(section_name)

    sections_node = self.root_node.find_child_by_name('n_sections')
#    insert_index = self._determine_section_insert_index(sections_node)

    parts = []
    if line_break_before:
      parts.append(self.line_break_str)
    parts.append(f'[{section_name}]')
    if line_break_after:
      parts.append(self.line_break_str)
    text = ''.join(parts)
    return self.add_node_from_text(sections_node,
                                   text,
                                   ( 'n_sections', 'n_section' ))
    
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

  def _find_global_section_node(self):
    global_section_node = self.root_node.find_child_by_name('n_global_section')
    if not global_section_node:
      raise bc_ini_error(f'missing node: "n_global_section"')
    return global_section_node
  
  def _find_global_key_value_node(self, key, raise_error = True):
    global_section_node = self._find_global_section_node()
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
