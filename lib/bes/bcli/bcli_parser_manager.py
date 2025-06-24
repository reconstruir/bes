#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse
import shlex

from ..system.check import check
from ..system.log import logger
from ..common.string_util import string_util

from .bcli_parser_tree import bcli_parser_tree
from .bcli_parser_factory_i import bcli_parser_factory_i
from .bcli_parser_error import bcli_parser_error

class bcli_parser_manager(object):

  _log = logger('bcli')

  def __init__(self):
    self._parser_factories = bcli_parser_tree()

  @classmethod
  def parse_path(self, path):
    if check.is_string_seq(path):
      return tuple(path)
    elif check.is_string(path):
      return tuple(path.split('/'))
    else:
      raise TypeError(f'path should be a str or str sequence: "{path}" - {type(path)}')
    
  def register_factory(self, parser_factory_class):
    if not issubclass(parser_factory_class, bcli_parser_factory_i):
      raise TypeError(f'parser_factory_class should be of type bcli_parser_factory_i instead of "{parser_factory_class}"')

    path = self.parse_path(parser_factory_class.path())
    self._parser_factories.set(path, parser_factory_class)

  def has_factory(self, path):
    path = self.parse_path(path)

    return self._parser_factories.get(path)
    
  def find_factory(self, path):
    path = self.parse_path(path)

    n = self._parser_factories.get(path)
    if n:
      return n.value
    return None

  def parse_args(self, s):
    check.check_string(s)

    parser, args = self._make_parser(s)
    return parser.parse_args(args)

  def format_help(self, s):
    check.check_string(s)

    parser, _ = self._make_parser(s)
    return parser.format_help()
  
  def _make_parser(self, s):
    self._log.log_d(f'_make_parser: s="{s}"')
    path, args = self._split_path_and_args(s)
    self._log.log_d(f'_make_parser: path={path} args={args}')

    parser_factory_class = self.find_factory(path)
    self._log.log_d(f'parser_factory_class={parser_factory_class}')
    if not parser_factory_class:
      raise bcli_parser_error(f'No parser class found: {" ".join(path)}')

    parser_factory = parser_factory_class()
    
    parser = argparse.ArgumentParser()

    parser_factory.add_arguments(parser)
    
    if parser_factory.has_sub_parsers():
      subparsers = parser.add_subparsers(help = 'commands', dest = '__bcli_command__')
      parser_factory.add_sub_parsers(subparsers)

    return parser, args
  
  def _split_path_and_args(self, s):
    check.check_string(s)

    parts = shlex.split(s)

    path, _, args = self._parser_factories.get_existing_prefix(parts)
    return path, args
    
check.register_class(bcli_parser_manager, include_seq = False)
