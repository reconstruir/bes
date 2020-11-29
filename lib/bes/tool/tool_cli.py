# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

## So for Python 3.8 we supress SyntaxWarning warnings
#if sys.version_info.major == 3 and sys.version_info.minor == 8:
#  warnings.filterwarnings('ignore', category = SyntaxWarning)

import argparse

from bes.cli.argparser_handler import argparser_handler
from bes.common.check import check
from bes.system.log import log
from bes.system.host import host
from bes.script.blurb import blurb
from bes.version.version_cli import version_cli

from bes.native_package.native_package_cli_args import native_package_cli_args
from bes.archive.archive_cli_args import archive_cli_args
from bes.computer_setup.computer_setup_cli_args import computer_setup_cli_args

command_parsers = [
  ( 'archive', 'archive_add_args', 'Deal with archive' ),
  ( 'computer_setup', 'computer_setup_add_args', 'Deal with computer setup' ),
  ( 'native_package', 'native_package_add_args', 'Deal with native packages' ),
]

if host.is_macos():
  from bes.macos.softwareupdater.softwareupdater_cli_args import softwareupdater_cli_args
  from bes.macos.command_line_tools.command_line_tools_cli_args import command_line_tools_cli_args
  from bes.macos.defaults.defaults_cli_args import defaults_cli_args
  command_parsers.extend([
    ( 'softwareupdater', 'softwareupdater_add_args', 'Deal with macos softwareupdate' ),
    ( 'command_line_tools', 'command_line_tools_add_args', 'Deal with command line tools' ),
    ( 'defaults', 'defaults_add_args', 'Deal with defaults' ),
  ])

if host.is_unix():
  from bes.unix.brew.brew_cli_args import brew_cli_args
  from bes.unix.brew_installer.brew_installer_cli_args import brew_installer_cli_args
  from bes.unix.shell.shell_cli_args import shell_cli_args
  from bes.unix.sudo.sudo_cli_args import sudo_cli_args
  command_parsers.extend([
    ( 'brew', 'brew_add_args', 'Deal with brew' ),
    ( 'brew_installer', 'brew_installer_add_args', 'Deal with brew install' ),
    ( 'shell', 'shell_add_args', 'Deal with shell' ),
    ( 'sudo', 'sudo_add_args', 'Deal with sudo' ),
  ])

class tool_cli(
  archive_cli_args,
  brew_cli_args,
  brew_installer_cli_args,
  command_line_tools_cli_args,
  computer_setup_cli_args,
  defaults_cli_args,
  native_package_cli_args,
  shell_cli_args,
  softwareupdater_cli_args,
  sudo_cli_args
):

  def __init__(self):
    log.add_logging(self, 'bes_tool')
    blurb.add_blurb(self, 'bes_tool')
    self.parser = argparse.ArgumentParser()

    commands_subparser = self.parser.add_subparsers(help = 'commands', dest = 'command_group')

    for p in command_parsers:
      self.add_command_group(commands_subparser, *p)

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
