#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse
import shlex
import dataclasses
import typing
import argparse

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
    self._log.log_d(f'register_factory: path={parser_factory_class.path()} parser_factory_class={parser_factory_class}')

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

  @dataclasses.dataclass
  class _parse_args_result(object):
    ns: argparse.Namespace
    path: str
    factory: bcli_parser_factory_i
  
  def parse_args(self, s):
    context = self._make_parser_context(s)
    ns = context.parser.parse_args(context.args)
    self._log.log_d(f'parse_args: ns={ns}')
    return self._parse_args_result(ns, context.path, context.factory)

  def format_help(self, s):
    context = self._make_parser_context(s)
    return context.parser.format_help()

  @dataclasses.dataclass
  class _parser_context(object):
    path: str
    parser: argparse.ArgumentParser
    args: dict
    factory: bcli_parser_factory_i
    
  def _make_parser_context(self, s):
    self._log.log_d(f'_make_parser_context: s="{s}"')
    path, args = self._split_path_and_args(s)
    self._log.log_d(f'_make_parser_context: path={path} args={args}')

    parser_factory_class = self.find_factory(path)
    self._log.log_d(f'parser_factory_class={parser_factory_class}')
    if not parser_factory_class:
      flat_path = '/'.join(path)
      raise bcli_parser_error(f'No parser class found for path: {flat_path}')

    parser_factory = parser_factory_class()
    
    parser = argparse.ArgumentParser()

    parser_factory.add_arguments(parser)
    
    if parser_factory.has_sub_parsers():
      subparsers = parser.add_subparsers(help = 'commands', dest = '__bcli_command_name__', required = True)
      parser_factory.add_sub_parsers(subparsers)

    return self._parser_context(path, parser, args, parser_factory)
  
  def _split_path_and_args(self, s):
    if check.is_string(s):
      parts = shlex.split(s)
    elif check.is_string_seq(s):
      parts = list(s)[:]
    
    path, _, args = self._parser_factories.get_existing_prefix(parts)
    return path, args

  def __repr__(self):
    return repr(self._parser_factories)
  
check.register_class(bcli_parser_manager, include_seq = False)
