#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class pip_cli_args(object):

  def __init__(self):
    pass
  
  def pip_add_args(self, subparser):

    # pip_version
    p = subparser.add_parser('ver', help = 'Print pip version.')
    self.__pip_add_common_args(p)
    p.add_argument('pip_exe', action = 'store', type = str, default = None,
                   help = 'The pip executable [ None ]')
    
    # pip_info
    p = subparser.add_parser('info', help = 'Print pip info.')
    self.__pip_add_common_args(p)
    p.add_argument('pip_exe', action = 'store', type = str, default = None,
                   help = 'The pip executable [ None ]')

    # pip_filename_info
    p = subparser.add_parser('filename_info', help = 'Print pip filename info.')
    self.__pip_add_common_args(p)
    p.add_argument('pip_exe', action = 'store', type = str, default = None,
                   help = 'The pip executable [ None ]')

    # pip_exe_for_python
    p = subparser.add_parser('exe_for_python', help = 'Find pip executable for a specific python exe.')
    self.__pip_add_common_args(p)
    p.add_argument('python_exe', action = 'store', type = str, default = None,
                   help = 'The python executable [ None ]')
    
  def __pip_add_common_args(self, p):
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
#    p.add_argument('-r', '--root-dir', action = 'store', default = None,
#                   help = 'The root directory where to install pip [ None ]')
#    p.add_argument('-p', '--python', action = 'store', default = None,
#                   dest = 'python_exe',
#                   help = 'The python executable to use [ None ]')
#    p.add_argument('name', action = 'store', type = str, default = None,
#                   help = 'The name for this pip installation [ None ]')
     
  def _command_pip(self, command, *args, **kargs):
    from .pip_cli_handler import pip_cli_handler
    return pip_cli_handler(kargs).handle_command(command)
