#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import ast

from collections import namedtuple

from bes.common.check import check
from bes.property.cached_property import cached_property

from .refactor_ast_node_type import refactor_ast_node_type

class refactor_ast_item(namedtuple('refactor_ast_item', 'source, node, node_type')):

  def __new__(clazz, source, node, node_type):
    check.check_refactor_ast_source(source)
    check.check_refactor_ast_node_type(node_type)

    return clazz.__bases__[0].__new__(clazz, source, node, node_type)

  @cached_property
  def segment(self):
    return ast.get_source_segment(self.source.text, self.node, padded = False)

  '''
  FunctionDef

    name is a raw string of the function name.

    args is an arguments node.

    body is the list of nodes inside the function.

    decorator_list is the list of decorators to be applied, stored outermost first (i.e. the first in the list will be applied last).

    returns is the return annotation.

  ClassDef


    name is a raw string for the class name

    bases is a list of nodes for explicitly specified base classes.

    keywords is a list of keyword nodes, principally for ‘metaclass’. Other keywords will be passed to the metaclass, as per PEP-3115.

    starargs and kwargs are each a single node, as in a function call. starargs will be expanded to join the list of base classes, and kwargs will be passed to the metaclass.

    body is a list of nodes representing the code within the class definition.

    decorator_list is a list of nodes, as in FunctionDef.

'''
  
  
check.register_class(refactor_ast_item, include_seq = False)
