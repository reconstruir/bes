#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check

from .vmware_preferences import vmware_preferences

class vmware_preferences_cli_handler(cli_command_handler):
  'vmware preferences cli handler.'

  def __init__(self, cli_args):
    super(vmware_preferences_cli_handler, self).__init__(cli_args)

  def set_value(self, filename, key, value):
    prefs = vmware_preferences(filename)
    prefs.set_value(key, value)
    return 0

  def get_value(self, filename, key):
    prefs = vmware_preferences(None)
    print(prefs.get_value(key))
    return 0
