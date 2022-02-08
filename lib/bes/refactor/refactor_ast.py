#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import ast

from bes.common.check import check
from bes.fs.file_util import file_util
from bes.text.text_search import text_search

from .refactor_ast_file import refactor_ast_file
from .refactor_ast_item import refactor_ast_item
from .refactor_ast_item_list import refactor_ast_item_list
from .refactor_ast_node_type import refactor_ast_node_type
from .refactor_ast_source import refactor_ast_source
from .refactor_files import refactor_files
from .refactor_options import refactor_options

class refactor_ast(object):

  @classmethod
  def resolve_nodes(clazz, files, node_type):
    'Resolve all python classes.'
    check.check_string_seq(files)
    check.check_refactor_ast_node_type(node_type)
    
    python_files = refactor_files.resolve_python_files(files)
    for r in python_files:
      print(f'{r}')
    return []

  @classmethod
  def grep(clazz, files, text, node_type, options = None):
    'Resolve all python classes.'
    check.check_string_seq(files)
    check.check_string(text)
    check.check_refactor_ast_node_type(node_type)
    check.check_refactor_options(options, allow_none = True)

    options = options or refactor_options()    
    result = refactor_ast_item_list()
    python_files = refactor_files.resolve_python_files(files)
    for filename in python_files:
      
      source = refactor_ast_source(filename)
      nodes = source.find_nodes(node_type)
      for node in nodes:
        item = refactor_ast_item(source, node, node_type)
        spans = text_search.find_all(item.name, text,
                                     word_boundary = options.word_boundary,
                                     word_boundary_chars = options.word_boundary_chars)
        if spans:
          #print(f'name={item.name} spans={spans}')
          result.append(item)
    return result
