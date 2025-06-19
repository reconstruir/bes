#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from ..system.log import logger

from .bcli_parser_tree import bcli_parser_tree

class bcli_parser_manager(object):

  _log = logger('bcli')

  def __init__(self):
    self._parser_classes = bcli_parser_tree()
    
  def register_parser(self, path, parser_class):
    check.check_string_seq(path)
    check.check_class(parser_class)

    self._parser_classes.set(path, parser_class)

  def has_parser(self, path):
    check.check_string_seq(path)

    return self._parser_classes.get(path)
    
  def find_parser(self, path):
    check.check_string_seq(path)

    return self._parser_classes.get(path)
    
check.register_class(bcli_parser_manager, include_seq = False)
