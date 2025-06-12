#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.Script import Script
from ..system.check import check
from bes.script.blurber import blurber

from .vmware_credentials import vmware_credentials
from .vmware_server_shell import vmware_server_shell
from .vmware_server_options import vmware_server_options

class bat_vmware_server_cli_handler(cli_command_handler):
  'vmware server cli handler.'

  def __init__(self, cli_args):
    super().__init__(cli_args, options_class = vmware_server_options)
    check.check_vmware_server_options(self.options)

  def shell(self, shell_args):
    check.check_string_seq(shell_args)
    
    args = []
    if self.options.port:
      args.extend([ '--port', self.options.port ])
    raise SystemExit(vmware_server_shell().main(args = args, shell_args = shell_args))
    return 0

  def set_credentials(self, username, password, num_tries):
    check.check_string(username)
    check.check_string(password)
    check.check_int(num_tries, allow_none = True)
    
    vmware_credentials.set_credentials(username, password, num_tries = num_tries)
    return 0
