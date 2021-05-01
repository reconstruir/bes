#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class pip_project_cli_args(object):

  def __init__(self):
    pass
  
  def pip_project_add_args(self, subparser):

    # pip_project_outdated
    p = subparser.add_parser('outdated', help = 'Print outdated packages.')
    self.__pip_project_add_common_args(p)
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The name for this pip project [ None ]')

    # pip_project_installed
    p = subparser.add_parser('installed', help = 'Print install packages.')
    self.__pip_project_add_common_args(p)
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The name for this pip project [ None ]')
    
    # pip_project_pip
    p = subparser.add_parser('pip', help = 'Run pip command.')
    self.__pip_project_add_common_args(p)
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The name for this pip project [ None ]')
    p.add_argument('args', action = 'store', default = [], nargs = '+',
                   help = 'The pip args. [ None ]')
    
  def __pip_project_add_common_args(self, p):
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('-r', '--root-dir', action = 'store', default = None,
                   help = 'The root directory where to install pip [ None ]')
    p.add_argument('-p', '--python-version', action = 'store', default = None,
                   dest = 'python_version',
                   help = 'The python version to use [ None ]')
    p.add_argument('-c', '--config', action = 'store', default = None,
                   dest = 'config_filename',
                   help = 'The config filename to use [ None ]')
     
  def _command_pip_project(self, command, *args, **kargs):
    from .pip_project_cli_handler import pip_project_cli_handler
    return pip_project_cli_handler(kargs).handle_command(command)
