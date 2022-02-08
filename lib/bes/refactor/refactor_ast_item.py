#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check

class refactor_ast_item(namedtuple('refactor_ast_item', 'filename, node')):

  def __new__(clazz, filename, node):
    check.check_string(filename)
    check.check_string(node)

    return clazz.__bases__[0].__new__(clazz, filename, node)

check.register_class(refactor_ast_item, include_seq = False)
