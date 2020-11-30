# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse
from abc import abstractmethod, ABCMeta

from .argparser_handler import argparser_handler
from bes.common.check import check
from bes.script.blurb import blurb
from bes.system.compat import with_metaclass
from bes.system.log import log
from bes.version.version_cli import version_cli

from .cli_command_list import cli_command_list

class cli(with_metaclass(ABCMeta, object)):

  def __init__(self, name):
    check.check_string(name)

    self.name = name
    log.add_logging(self, self.name)
    blurb.add_blurb(self, self.name)
    self.parser = argparse.ArgumentParser()

    from bes.cli.cli_help_cli_args import cli_help_cli_args
    cli_help_cli_args.parser = self.parser
    
    self.commands_subparser = self.parser.add_subparsers(help = 'commands', dest = 'command_group')

    command_groups = cli_command_list(self.command_group_list())
    command_groups.sort(key = lambda item: item.name)

    commands = cli_command_list(self.command_list())
    commands.sort(key = lambda item: item.name)

    all_handlers = cli_command_list()
    all_handlers.extend(command_groups)
    all_handlers.extend(commands)
    
    handler_class_name = '{}_handler_superclass'.format(name)
    handler_class = all_handlers.make_handler_superclass(handler_class_name)
    self.handler_object = handler_class()
    
    for command_group in command_groups:
      self._add_command_group(self.commands_subparser,
                              command_group.name,
                              command_group.add_args_function,
                              command_group.description)

    for command in commands:
      self._add_command(self.commands_subparser,
                        command.name,
                        command.add_args_function,
                        command.description)

  @abstractmethod
  def command_list(self):
    'Return a list of commands for this cli.'
    raise NotImplemented('command_list')

  @abstractmethod
  def command_group_list(self):
    'Return a list of command groups for this cli.'
    raise NotImplemented('command_group_list')

  def main(self):
    return argparser_handler.main(self.name, self.parser, self.handler_object)

  def _add_command_group(self, commands_subparser, command_group, arg_adder, help_blurb):
    parser = commands_subparser.add_parser(command_group, help = help_blurb)
    subparsers_help_blurb = '%s_commands' % (command_group)
    subparsers = parser.add_subparsers(help = subparsers_help_blurb, dest = 'command')
    adder = getattr(self.handler_object, arg_adder)
    adder(subparsers)

  def _add_command(self, commands_subparser, command_name, arg_adder, help_blurb):
    parser = commands_subparser.add_parser(command_name, help = help_blurb)
    adder = getattr(self.handler_object, arg_adder)
    adder(parser)
