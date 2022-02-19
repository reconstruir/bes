#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import ast

from collections import namedtuple

from bes.fs.file_util import file_util
from bes.fs.file_check import file_check
from bes.common.check import check

from .refactor_ast_node_type import refactor_ast_node_type
from .refactor_ast_item import refactor_ast_item
from .refactor_ast_util import refactor_ast_util

class refactor_ast_file(object):

  @classmethod
  def find_nodes(clazz, filename, node_type):
    check.check_refactor_ast_node_type(node_type)

    filename = file_check.check_file(filename)

    source_code = file_util.read(filename, codec = 'utf-8')
    tree = ast.parse(source_code)

    nodes = refactor_ast_util.find_nodes(tree, node_type)
    return nodes
