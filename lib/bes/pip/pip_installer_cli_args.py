#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class pip_installer_cli_args(object):

  def __init__(self):
    pass
  
  def pip_installer_add_args(self, subparser):

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
    
  def _command_pip_installer(self, command, *args, **kargs):
    from .pip_installer_cli_handler import pip_installer_cli_handler
    return pip_installer_cli_handler(kargs).handle_command(command)
