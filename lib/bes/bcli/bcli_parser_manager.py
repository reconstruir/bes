#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse
import shlex

from ..system.check import check
from ..system.log import logger
from ..common.string_util import string_util

from .bcli_parser_tree import bcli_parser_tree
from .bcli_parser_maker_i import bcli_parser_maker_i
from .bcli_parser_error import bcli_parser_error

class bcli_parser_manager(object):

  _log = logger('bcli')

  def __init__(self):
    self._parser_factories = bcli_parser_tree()
    
  def register_parser(self, path, parser_factory_class):
    check.check_string_seq(path)

    if not issubclass(parser_factory_class, bcli_parser_maker_i):
      raise TypeError(f'parser_factory_class should be of type bcli_parser_maker_i instead of "{parser_factory_class}"')

    self._parser_factories.set(path, parser_factory_class)

  def has_parser(self, path):
    check.check_string_seq(path)

    return self._parser_factories.get(path)
    
  def find_parser_factory(self, path):
    check.check_string_seq(path)

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

    parser_factory_class = self.find_parser_factory(path)
    self._log.log_d(f'parser_factory_class={parser_factory_class}')
    if not parser_factory_class:
      raise bcli_parser_error(f'No parser class found: {" ".join(path)}')

    parser_factory = parser_factory_class()
    
    parser = argparse.ArgumentParser()

    parser_factory.add_arguments(parser)
    
    if parser_factory.has_sub_parsers():
      subparsers = parser.add_subparsers() # FIXME: maybe need something like this: dest='area', required=True)
      parser_factory.add_sub_parsers(subparsers)

    return parser, args
  
  def _split_path_and_args(self, s):
    check.check_string(s)

    parts = shlex.split(s)

    path, _, args = self._parser_factories.get_existing_prefix(parts)
    return path, args
    
check.register_class(bcli_parser_manager, include_seq = False)
