#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.cli.cli_command_handler import cli_command_handler
from ..system.check import check
from bes.fs.file_util import file_util
from bes.text.text_table import text_table

from .bat_vmware_preferences import bat_vmware_preferences

class bat_vmware_preferences_cli_handler(cli_command_handler):
  'vmware preferences cli handler.'

  def __init__(self, cli_args):
    super(bat_vmware_preferences_cli_handler, self).__init__(cli_args)

  def set_value(self, filename, key, value, backup):
    check.check_string(filename, allow_none = True)
    check.check_string(key)
    check.check_string(value)
    check.check_bool(backup)
    
    prefs = bat_vmware_preferences(filename, backup = backup)
    prefs.set_value(key, value)
    return 0

  def get_value(self, filename, key):
    check.check_string(filename, allow_none = True)
    check.check_string(key)

    prefs = bat_vmware_preferences(filename)
    print(prefs.get_value(key))
    return 0

  def print_values(self, filename, verbose):
    check.check_string(filename, allow_none = True)
    check.check_bool(verbose)

    prefs = bat_vmware_preferences(filename)
    values = sorted(prefs.values().items())
    if verbose:
      print('{}:'.format(prefs.filename))
    tt = text_table(data = values)
    tt.set_labels( ( 'KEY', 'VALUE' ) )
    print(tt)
    return 0
  
