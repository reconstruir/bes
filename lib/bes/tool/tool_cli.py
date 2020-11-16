# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

## So for Python 3.8 we supress SyntaxWarning warnings
#if sys.version_info.major == 3 and sys.version_info.minor == 8:
#  warnings.filterwarnings('ignore', category = SyntaxWarning)

import argparse

from bes.cli.argparser_handler import argparser_handler
from bes.common.check import check
from bes.system.log import log
from bes.script.blurb import blurb
from bes.version.version_cli import version_cli

from bes.unix.brew.brew_cli_args import brew_cli_args
from bes.unix.sudo.sudo_cli_args import sudo_cli_args

class tool_cli(
  brew_cli_args,
  sudo_cli_args
):

  def __init__(self):
    log.add_logging(self, 'bes_tool')
    blurb.add_blurb(self, 'bes_tool')
    self.parser = argparse.ArgumentParser()

    commands_subparser = self.parser.add_subparsers(help = 'commands', dest = 'command_group')

    self.add_command_group(commands_subparser, 'brew', 'brew_add_args', 'Deal with brew')
    self.add_command_group(commands_subparser, 'sudo', 'sudo_add_args', 'Deal with sudo')

    # version
    version_parser = commands_subparser.add_parser('version', help = 'Version a build to a build list.')
    version_cli.arg_sub_parser_add_arguments(version_parser)

  def _command_version(self, print_all, brief):
    version_cli.print_everything(
      'bes',
      dependencies = [],
      brief = brief,
      print_all = print_all
    )
    return 0

  def main(self):
    return argparser_handler.main('bes_tool', self.parser, self)

  def add_command_group(self, commands_subparser, command_group, arg_adder, help_blurb):
    parser = commands_subparser.add_parser(command_group, help = help_blurb)
    subparsers_help_blurb = '%s_commands' % (command_group)
    subparsers = parser.add_subparsers(help = subparsers_help_blurb, dest = 'command')
    adder = getattr(self, arg_adder)
    adder(subparsers)

  @classmethod
  def run(clazz):
    raise SystemExit(tool_cli().main())
