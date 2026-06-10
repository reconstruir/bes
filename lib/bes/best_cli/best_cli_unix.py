# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_command import cli_command

from bes.unix.sudo.sudo_cli_args import sudo_cli_args

UNIX_COMMAND_GROUPS = [
  cli_command('sudo', 'sudo_add_args', 'Deal with sudo', sudo_cli_args),
]
