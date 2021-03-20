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

    # pip_filename_info
    p = subparser.add_parser('filename_info', help = 'Print pip filename info.')
    p.add_argument('pip_exe', action = 'store', type = str, default = None,
                   help = 'The pip executable [ None ]')
    
  def _command_pip(self, command, *args, **kargs):
    from .pip_cli_handler import pip_cli_handler
    return pip_cli_handler(kargs).handle_command(command)
