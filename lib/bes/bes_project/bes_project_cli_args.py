#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class bes_project_cli_args(object):

  def __init__(self):
    pass
  
  def bes_project_add_args(self, subparser):

    # ensure
    p = subparser.add_parser('ensure', help = 'Ensure a bes is setup.')
    self.__bes_project_add_common_args(p)
    p.add_argument('--version', action = 'append', type = str, default = [],
                   dest = 'versions',
                   help = 'The version of python to use.  Multiple versions can be used along with "all" and "latest" [ None ]')
    p.add_argument('--requirements-dev', action = 'store', type = str, default = None,
                   help = 'The optional requirements-dev.txt file [ None ]')
    p.add_argument('requirements', action = 'store', type = str, default = None,
                   help = 'The requirements.txt file [ None ]')

    # activate_script
    p = subparser.add_parser('activate_script', help = 'Print the activate script for the virtual env.')
    self.__bes_project_add_common_args(p)
    p.add_argument('version', action = 'store', type = str, default = None,
                   help = 'The version of python [ None ]')
    p.add_argument('--variant', action = 'store', type = str, default = None,
                   help = 'The virtual env variant (csh, fish, ps1) [ None ]')
    
  def __bes_project_add_common_args(self, p):
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('-r', '--root-dir', action = 'store', default = None,
                   help = 'The root directory where to install pip [ None ]')
     
  def _command_bes_project(self, command, *args, **kargs):
    from .bes_project_cli_handler import bes_project_cli_handler
    return bes_project_cli_handler(kargs).handle_command(command)
