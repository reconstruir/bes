#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from ..system.log import logger
from ..common.string_util import string_util

from .bcli_parser_tree import bcli_parser_tree
from .bcli_parser_maker_i import bcli_parser_maker_i

class bcli_parser_manager(object):

  _log = logger('bcli')

  def __init__(self):
    self._parser_classes = bcli_parser_tree()
    
  def register_parser(self, path, parser_class):
    check.check_string_seq(path)

    if not issubclass(parser_class, bcli_parser_maker_i):
      raise TypeError(f'parser_class should be of type bcli_parser_maker_i instead of "{parser_class}"')

    self._parser_classes.set(path, parser_class)

  def has_parser(self, path):
    check.check_string_seq(path)

    return self._parser_classes.get(path)
    
  def find_parser(self, path):
    check.check_string_seq(path)

    return self._parser_classes.get(path)

  @classmethod
  def _split_path_and_args(clazz, s):
    check.check_string(s)

    parts = string_util.split_by_white_space(s)
    path = []
    args = []
    while True:
      if not parts:
        break
      if not parts[0].startswith('-'):
        path.append(parts.pop(0))
      else:
        break
    if parts:
      args = parts
    return path, ' '.join(args)
    
check.register_class(bcli_parser_manager, include_seq = False)
