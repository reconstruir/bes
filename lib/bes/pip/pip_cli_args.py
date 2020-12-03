#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class pip_cli_args(object):

  def __init__(self):
    pass
  
  def pip_add_args(self, subparser):

    # pip_version
    p = subparser.add_parser('ver', help = 'Print pip version.')
    p.add_argument('py_exe', action = 'store', type = str, default = None,
                   help = 'The python executable [ None ]')
    
    # pip_info
    p = subparser.add_parser('info', help = 'Print pip info.')
    p.add_argument('py_exe', action = 'store', type = str, default = None,
                   help = 'The python executable [ None ]')

    # pip_present
    p = subparser.add_parser('present', help = 'Return 0 if pip is present for the python executable.')
    p.add_argument('py_exe', action = 'store', type = str, default = None,
                   help = 'The python executable [ None ]')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   default = False, help = 'Verbose output')

    # pip_update
    p = subparser.add_parser('update', help = 'Update pip to a specific version or install it if needed.')
    p.add_argument('py_exe', action = 'store', type = str, default = None,
                   help = 'The python executable [ None ]')
    p.add_argument('pip_version', action = 'store', type = str, default = None,
                   help = 'The pip version [ None ]')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   default = False, help = 'Verbose output')

    # pip_uninstall
    p = subparser.add_parser('uninstall', help = 'Uninstall pip.')
    p.add_argument('py_exe', action = 'store', type = str, default = None,
                   help = 'The python executable [ None ]')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   default = False, help = 'Verbose output')
    
  def _command_pip(self, command, *args, **kargs):
    from .pip_cli_command import pip_cli_command
    return pip_cli_command.handle_command(command, **kargs)
  