#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class vmware_preferences_cli_args(object):

  def __init__(self):
    pass
  
  def vmware_preferences_add_args(self, subparser):

    # set_value
    p = subparser.add_parser('set_value', help = 'Set a vmware preferences value.')
    p.add_argument('-f', '--filename', action = 'store', type = str, default = None,
                   help = 'The preferences filename [ ]')
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
    
  def _command_vmware_preferences(self, command, *args, **kargs):
    from .vmware_preferences_cli_handler import vmware_preferences_cli_handler
    return vmware_preferences_cli_handler(kargs).handle_command(command)
