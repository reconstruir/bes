
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from bes.btl.btl_document import btl_document

from .bc_ini_lexer import bc_ini_lexer
from .bc_ini_parser import bc_ini_parser

class bc_ini_document(btl_document):

  def __init__(self, text, parser_options = None):
    lexer = bc_ini_lexer()
    parser = bc_ini_parser(lexer)
    super().__init__(parser, text, parser_options = parser_options)

  def get_value(self, key):
    check.check_string(key)

  def set_value(self, key, value):
    check.check_string(key)
    check.check_string(value)

  def remove_value(self, key):
    check.check_string(key)
    
  def get_section_value(self, section_name, key):
    check.check_string(section_name)
    check.check_string(key)

    sections_node = self.root_node.find_child_by_name('n_sections')
    assert sections_node
    section_node = sections_node.find_child_by_token('n_section',
                                                     't_section_name',
                                                     section_name)
    assert section_node
    kv_node = section_node.find_grandchild_by_token('n_key_value',
                                                    'n_key',
                                                    't_key',
                                                    key)
    assert kv_node
    return kv_node.children[1].token.value
    
  def set_section_value(self, section_name, key, value):
    check.check_string(section_name)
    check.check_string(key)
    check.check_string(value)

  def add_section(self, section_name):
    check.check_string(section_name)

  def remove_section(self, section_name):
    check.check_string(section_name)
    
check.register_class(bc_ini_document, include_seq = False)
