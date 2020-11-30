# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse
from abc import abstractmethod, ABCMeta

from .argparser_handler import argparser_handler
from bes.common.check import check
from bes.script.blurb import blurb
from bes.system.compat import with_metaclass
from bes.system.log import log
from bes.version.version_cli import version_cli

from .cli_item_list import cli_item_list

class _version_cli_args(object):
  
  def _command_version(self, command, *args, **kargs):
    assert command == None
    assert 'print_all' in kargs
    assert 'brief' in kargs
    version_cli.print_everything(self.version_module_name,
                                 dependencies = self.version_dependencies,
                                 brief = kargs['brief'],
                                 print_all = kargs['print_all'])
    return 0

class cli(with_metaclass(ABCMeta, object)):

  def __init__(self, name, version_module_name, version_dependencies = None):
    check.check_string(name)
    check.check_string(version_module_name)
    check.check_string_seq(version_dependencies, allow_none = True)
    
    self.name = name
    log.add_logging(self, self.name)
    blurb.add_blurb(self, self.name)
    self.parser = argparse.ArgumentParser()

    commands_subparser = self.parser.add_subparsers(help = 'commands', dest = 'command_group')
    items = cli_item_list(self.tool_item_list())
    handler_class_name = '{}_handler_superclass'.format(name)
    _version_cli_args.version_module_name = version_module_name
    _version_cli_args.version_dependencies = version_dependencies
    handler_class = items.make_handler_superclass(_version_cli_args, handler_class_name)
    self.handler_object = handler_class()
    for item in items:
      self._add_command_group(commands_subparser,
                              item.name,
                              item.add_args_function,
                              item.description)

    # version
    version_parser = commands_subparser.add_parser('version', help = 'Print version information.')
    version_cli.arg_sub_parser_add_arguments(version_parser)
    
  @abstractmethod
  def tool_item_list(self):
    'Return a list of tool items for this cli.'
    raise NotImplemented('tool_item_list')

  def main(self):
    return argparser_handler.main(self.name, self.parser, self.handler_object)

  def _add_command_group(self, commands_subparser, command_group, arg_adder, help_blurb):
    parser = commands_subparser.add_parser(command_group, help = help_blurb)
    subparsers_help_blurb = '%s_commands' % (command_group)
    subparsers = parser.add_subparsers(help = subparsers_help_blurb, dest = 'command')
    adder = getattr(self.handler_object, arg_adder)
    adder(subparsers)

    
