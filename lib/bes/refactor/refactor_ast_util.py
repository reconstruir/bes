#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check

import ast

from .refactor_ast_node_type import refactor_ast_node_type

class refactor_ast_util(object):

  @classmethod
  def _find_nodes_by_ast_class(clazz, node, ast_class):
    result = []
    for next_node in ast.walk(node):
      if isinstance(next_node, ast_class):
        result.append(next_node)
    return result
  
  @classmethod
  def find_nodes(clazz, node, node_type):
    check.check_refactor_ast_node_type(node_type)
    
    if node_type == refactor_ast_node_type.CLASS:
      result = clazz._find_nodes_by_ast_class(node, ast.ClassDef)
    elif node_type == refactor_ast_node_type.FUNCTION:
      result = clazz._find_nodes_by_ast_class(node, ast.FunctionDef)
    elif node_type == refactor_ast_node_type.CLASS_FUNCTION:
      class_nodes = clazz._find_nodes_by_ast_class(node, ast.ClassDef)
      result = []
      for next_class_node in class_nodes:
        result.extend(clazz._find_nodes_by_ast_class(node, ast.FunctionDef))
    else:
      raise ValueError(f'Unhandled node_type {node_type}')
    return result
