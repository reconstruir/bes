#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check

from .vmware_util import vmware_util

class vmware_cli_handler(cli_command_handler):
  'vmware preferences cli handler.'

  def __init__(self, cli_args):
    super(vmware_cli_handler, self).__init__(cli_args)

  def is_running(self):
    return 0 if vmware_util.is_running() else 1

  def ensure_running(self):
    vmware_util.ensure_running()
    return 0
