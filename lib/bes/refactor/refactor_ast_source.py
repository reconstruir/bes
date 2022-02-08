#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import ast

from collections import namedtuple

from bes.common.check import check
from bes.property.cached_property import cached_property
from bes.fs.file_util import file_util
from bes.fs.file_check import file_check

from .refactor_ast_node_type import refactor_ast_node_type
from .refactor_ast_util import refactor_ast_util

class refactor_ast_source(namedtuple('refactor_ast_source', 'filename')):

  def __new__(clazz, filename):
    filename = file_check.check_file(filename)

    return clazz.__bases__[0].__new__(clazz, filename)

  @cached_property
  def text(self):
    return file_util.read(self.filename, codec = 'utf-8')
  
  @cached_property
  def lines(self):
    return self.text.splitlines()

  @cached_property
  def tree(self):
    return ast.parse(self.text)

  def find_nodes(self, node_type):
    check.check_refactor_ast_node_type(node_type)

    return refactor_ast_util.find_nodes(self.tree, node_type)
  
check.register_class(refactor_ast_source, include_seq = False)
