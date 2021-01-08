#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.Script import Script
from bes.common.check import check
from bes.script.blurber import blurber

from .vmware_vmrest import vmware_vmrest
from .vmware_vmrest_options import vmware_vmrest_options
from .vmware_vmrest_app import vmware_vmrest_app

class vmware_vmrest_cli_command(cli_command_handler):
  'python installer cli handler.'

  def __init__(self, cli_args):
    super(vmware_vmrest_cli_command, self).__init__(cli_args, options_class = vmware_vmrest_options)
    check.check_vmware_vmrest_options(self.options)

  def shell(self):
    args = []
    if self.options.port:
      args.extend([ '--port', self.options.port ])
    raise SystemExit(vmware_vmrest_app().main(args = args))
    return 0
