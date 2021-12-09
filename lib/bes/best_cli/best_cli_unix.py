 # -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_command import cli_command

from bes.unix.brew.brew_cli_args import brew_cli_args
from bes.unix.brew_installer.brew_installer_cli_args import brew_installer_cli_args
from bes.unix.shell.shell_cli_args import shell_cli_args
from bes.unix.sudo.sudo_cli_args import sudo_cli_args

UNIX_COMMAND_GROUPS = [
  cli_command('brew', 'brew_add_args', 'Deal with brew', brew_cli_args),
  cli_command('brew_installer', 'brew_installer_add_args', 'Deal with brew install', brew_installer_cli_args),
  cli_command('shell', 'shell_add_args', 'Deal with shell', shell_cli_args),
  cli_command('sudo', 'sudo_add_args', 'Deal with sudo', sudo_cli_args),
]
