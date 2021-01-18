#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check

from .vmware_app import vmware_app

class vmware_app_cli_handler(cli_command_handler):
  'vmware app cli handler.'

  def __init__(self, cli_args):
    super(vmware_app_cli_handler, self).__init__(cli_args)
    self._app = vmware_app()

  def is_installed(self):
    return 0 if self._app.is_installed() else 1

  def is_running(self):
    return 0 if self._app.is_running() else 1
  
  def ensure_running(self):
    self._app.ensure_running()
    return 0
