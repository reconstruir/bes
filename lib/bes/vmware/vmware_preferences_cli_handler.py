#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check
from bes.fs.file_util import file_util
from .vmware_preferences import vmware_preferences

class vmware_preferences_cli_handler(cli_command_handler):
  'vmware preferences cli handler.'

  def __init__(self, cli_args):
    super(vmware_preferences_cli_handler, self).__init__(cli_args)

  def set_value(self, filename, key, value, backup):
    check.check_string(filename)
    check.check_string(key)
    check.check_string(value)
    check.check_bool(backup)
    
    prefs = vmware_preferences(filename, backup = backup)
    prefs.set_value(key, value)
    return 0

  def get_value(self, filename, key):
    check.check_string(filename)
    check.check_string(key)

    prefs = vmware_preferences(None)
    print(prefs.get_value(key))
    return 0
