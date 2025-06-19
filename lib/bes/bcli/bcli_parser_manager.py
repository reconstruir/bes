#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..common.node import node
from ..system.check import check
from ..system.log import logger

class bcli_parser_manager(object):

  _log = logger('bcli')

  def __init__(self):
    self._parser_classes = node('root')
    
  def register_parser(self, parser_path, parser_class):
    check.check_string(parser_path)
    check.check_class(parser_class)

    n = self._parser_classes.ensure_path(parser_path)
    n.data = parser_class

  def find_parser(self, parser_path):
    check.check_string(parser_path)

    n = self._parser_classes.find_child_by_path_data(parser_path)
    print(f'n={n}')
    
check.register_class(bcli_parser_manager, include_seq = False)
