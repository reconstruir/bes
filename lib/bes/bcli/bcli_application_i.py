# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import pprint
import sys

from abc import abstractmethod
from abc import ABC

from ..system.check import check
from ..script.blurb import blurb
from ..system.log import logger

from .bcli_parser_manager import bcli_parser_manager
from .bcli_parser_error import bcli_parser_error
from .bcli_options import bcli_options

class bcli_application_i(ABC):

  _log = logger('bcli')
  
  def __init__(self):
    name = self.name()
    check.check_string(name)

    blurb.add_blurb(self, name)

    self._parser_manager = bcli_parser_manager()
    for next_parser_factory in self.parser_factories():
      self._parser_manager.register_factory(next_parser_factory)

  @abstractmethod
  def name(self):
    raise NotImplementedError(f'name')
      
  @abstractmethod
  def parser_factories(self):
    raise NotImplementedError(f'parser_factories')
    
  def run(self, args):
    self._log.log_d(f'run: tree=\n-----\n{repr(self._parser_manager)}\n------')
    self._log.log_d(f'run: args="{args}"')
    parse_rv = self._parser_manager.parse_args(args)
    self._log.log_d(f'run: parse_rv={parse_rv}')
    ns_dict = copy.deepcopy(parse_rv.ns.__dict__)
    command_name = ns_dict['__bcli_command_name__']
    self._log.log_d(f'run: command_name={command_name}')
    del ns_dict['__bcli_command_name__']
    self._log.log_d(f'run: ns_dict={pprint.pformat(ns_dict)}')
    command_path = '_'.join(parse_rv.path)
    command_handler_name = f'_command_{command_path}_{command_name}'
    self._log.log_d(f'run: command_handler_name={command_handler_name}')

    handler_class = parse_rv.factory.handler_class()
    handler_instance = handler_class()
    command_handler = getattr(handler_instance, command_handler_name, None)
    self._log.log_d(f'run: command_handler={command_handler}')
    if not command_handler:
      raise bcli_parser_error(f'command handler: "{command_handler_name}" not found in {self}')

    new_ns_dict = self._extract_options(parse_rv.factory.options_class(), ns_dict)
    
    rv = command_handler(**new_ns_dict)
    return rv

  @classmethod
  def _extract_options(clazz, options_class, ns_dict):
    check.check_class(options_class, allow_none = True)
    check.check_dict(ns_dict)
    
    if not options_class:
      new_ns_dict = copy.deepcopy(ns_dict)
      new_ns_dict['options'] = None
      return new_ns_dict
    
    options = options_class()
    check.check_bcli_options(options)
    new_ns_dict = {}
    for name, value in ns_dict.items():
      if options.has_option(name):
        setattr(options, name, value)
      else:
        new_ns_dict[name] = value
    new_ns_dict['options'] = options
    return new_ns_dict

  @classmethod
  def main(clazz):
    app = clazz()
    args = sys.argv[1:]
    rv = app.run(args)
    return rv
