#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from ..system.log import logger

from .bcli_parser_tree import bcli_parser_tree

class bcli_parser_manager(object):

  _log = logger('bcli')

  def __init__(self):
    self._parser_classes = bcli_parser_tree()
    
  def register_parser(self, parser_path, parser_class):
    check.check_string(parser_path)
    check.check_class(parser_class)

    n = self._parser_classes.set(parser_path, parser_class)
#    n.data = parser_class

  def find_parser(self, parser_path):
    check.check_string(parser_path)

    return self._parser_classes.get(parser_path)
    
check.register_class(bcli_parser_manager, include_seq = False)
