# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_command import cli_command

from bes.macos.command_line_tools.command_line_tools_cli_args import command_line_tools_cli_args
from bes.macos.defaults.defaults_cli_args import defaults_cli_args
from bes.macos.scutil.scutil_cli_args import scutil_cli_args
from bes.macos.softwareupdater.softwareupdater_cli_args import softwareupdater_cli_args

MACOS_COMMAND_GROUPS = [
  cli_command('command_line_tools', 'command_line_tools_add_args', 'Deal with command line tools', command_line_tools_cli_args),
  cli_command('defaults', 'defaults_add_args', 'Deal with defaults', defaults_cli_args),
  cli_command('scutil', 'scutil_add_args', 'Deal with scutil', scutil_cli_args),
  cli_command('softwareupdater', 'softwareupdater_add_args', 'Deal with macos softwareupdate', softwareupdater_cli_args),
]
