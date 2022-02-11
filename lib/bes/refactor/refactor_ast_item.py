#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import ast
import os
import re

from collections import namedtuple

from bes.common.check import check
from bes.property.cached_property import cached_property
from bes.text.text_line import text_line
from bes.text.text_insert import text_insert

from .refactor_ast_node_type import refactor_ast_node_type

class refactor_ast_item(namedtuple('refactor_ast_item', 'source, node, node_type')):

  def __new__(clazz, source, node, node_type):
    check.check_refactor_ast_source(source)
    check.check_refactor_ast_node_type(node_type)

    return clazz.__bases__[0].__new__(clazz, source, node, node_type)

  @cached_property
  def segment(self):
    return ast.get_source_segment(self.source.text, self.node, padded = False)

  @cached_property
  def filename(self):
    return self.source.filename

  @cached_property
  def line_number(self):
    return self.node.lineno

  @cached_property
  def end_line_number(self):
    return self.node.end_lineno

  @cached_property
  def name(self):
    return self.node.name
  
  @cached_property
  def snippet(self):
    return os.linesep.join(self.source.lines[self.line_number - 1 : self.end_line_number])

  @cached_property
  def snippet_lines(self):
    lines = self.source.lines[self.line_number - 1 : self.end_line_number]
    result = []
    for line_number, line in enumerate(lines, start = self.line_number):
      result.append(text_line(line_number, line))
    return result
  
  @cached_property
  def definition(self):
    if isinstance(self.node, ast.FunctionDef):
      return self._definition_for_function()
    elif isinstance(self.node, ast.ClassDef):
      return self._definition_for_class()
    else:
      assert False

  @cached_property
  def definition_lines(self):
    lines = self.definition.splitlines()
    result = []
    for line_number, line in enumerate(lines, start = self.line_number):
      result.append(text_line(line_number, line))
    return result
      
  def _definition_for_function(self):
    f = re.findall(rf'.*(def\s+{self.name}\s*\(.*\)):.*', self.snippet, re.DOTALL)
    if not f:
      return None
    if len(f) != 1:
      return None
    return f[0]

  def definition_add_arg(self, arg_name):
    if not self.definition:
      return None
    i = self.definition.rfind(')')
    if i < 0:
      return None
    return text_insert.insert(self.definition, i, f', {arg_name}')
  
  def _definition_for_class(self):
    return 'bar'
    
  #  Get source code segment of the source that generated node. If some location information (lineno, end_lineno, col_offset, or end_col_offset) is missing, return None.
  
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
