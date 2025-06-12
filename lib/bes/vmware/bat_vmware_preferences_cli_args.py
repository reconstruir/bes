#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class bat_vmware_preferences_cli_args(object):

  def __init__(self):
    pass
  
  def vmware_preferences_add_args(self, subparser):

    # set_value
    p = subparser.add_parser('set_value', help = 'Set a vmware preferences value.')
    p.add_argument('-f', '--filename', action = 'store', type = str, default = None,
                   help = 'The preferences filename [ ]')
    p.add_argument('-b', '--backup', action = 'store_true', default = False,
                   help = 'Make a backup of the preferences file if applicable [ ]')
    p.add_argument('key', action = 'store', type = str, default = None,
                   help = 'The pref key [ ]')
    p.add_argument('value', action = 'store', type = str, default = None,
                   help = 'The pref value [ ]')

    # get_value
    p = subparser.add_parser('get_value', help = 'Get a vmware preferences value.')
    p.add_argument('-f', '--filename', action = 'store', type = str, default = None,
                   help = 'The preferences filename [ ]')
    p.add_argument('key', action = 'store', type = str, default = None,
                   help = 'The pref key [ ]')

    # print
    p = subparser.add_parser('print_values', help = 'Print vmware preferences.')
    p.add_argument('-f', '--filename', action = 'store', type = str, default = None,
                   help = 'The preferences filename [ ]')
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ ]')
    
  def _command_vmware_preferences(self, command, *args, **kargs):
    from .bat_vmware_preferences_cli_handler import bat_vmware_preferences_cli_handler
    return bat_vmware_preferences_cli_handler(kargs).handle_command(command)
