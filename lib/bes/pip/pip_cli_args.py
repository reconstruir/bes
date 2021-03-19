#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class pip_cli_args(object):

  def __init__(self):
    pass
  
  def pip_add_args(self, subparser):

    # pip_version
    p = subparser.add_parser('ver', help = 'Print pip version.')
    p.add_argument('pip_exe', action = 'store', type = str, default = None,
                   help = 'The pip executable [ None ]')
    
    # pip_info
    p = subparser.add_parser('info', help = 'Print pip info.')
    p.add_argument('pip_exe', action = 'store', type = str, default = None,
                   help = 'The pip executable [ None ]')

#    # pip_present
#    p = subparser.add_parser('present', help = 'Return 0 if pip is present for the python executable.')
#    p.add_argument('py_exe', action = 'store', type = str, default = None,
#                   help = 'The python executable [ None ]')
#    p.add_argument('-v', '--verbose', action = 'store_true',
#                   default = False, help = 'Verbose output')

  def _command_pip(self, command, *args, **kargs):
    from .pip_cli_handler import pip_cli_handler
    return pip_cli_handler(kargs).handle_command(command)
