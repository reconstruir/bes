#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class properties_file_cli_args(object):

  def __init__(self):
    pass
  
  def properties_file_add_args(self, subparser):
    # properties_set
    p = subparser.add_parser('set', help = 'Set a property in a property file.')
    p.add_argument('filename', action = 'store', default = None, type = str,
                   help = 'The property filename. [ None ]')
    p.add_argument('key', action = 'store', default = None, type = str,
                   help = 'The property key. [ None ]')
    p.add_argument('value', action = 'store', default = None, type = str,
                   help = 'The property value. [ None ]')

    # properties_get
    p = subparser.add_parser('get', help = 'Get a property from a property file.')
    p.add_argument('filename', action = 'store', default = None, type = str,
                   help = 'The property filename. [ None ]')
    p.add_argument('key', action = 'store', default = None, type = str,
                   help = 'The property key. [ None ]')

    # properties_bump_version
    p = subparser.add_parser('bump_version', help = 'Bump a property version.')
    p.add_argument('filename', action = 'store', default = None, type = str,
                   help = 'The property filename. [ None ]')
    p.add_argument('key', action = 'store', default = None, type = str,
                   help = 'The property key. [ None ]')
    p.add_argument('-c', '--component', action = 'store', default = 'revision', type = str,
                   choices = [ 'major', 'minor', 'revision' ],
                   help = 'Which version component to bump. [ None ]')
    
    # properties_change_version
    p = subparser.add_parser('change_version', help = 'Change a property version.')
    p.add_argument('filename', action = 'store', default = None, type = str,
                   help = 'The property filename. [ None ]')
    p.add_argument('key', action = 'store', default = None, type = str,
                   help = 'The property key. [ None ]')
    p.add_argument('component', action = 'store', default = 'revision', type = str,
                   choices = [ 'major', 'minor', 'revision' ],
                   help = 'Which version component to change. [ None ]')
    p.add_argument('value', action = 'store', default = None, type = str,
                   help = 'The new value. [ None ]')

  def _command_properties_file(self, command, *args, **kargs):
    from .properties_file_cli_handler import properties_file_cli_handler
    return properties_file_cli_handler(kargs).handle_command(command)
