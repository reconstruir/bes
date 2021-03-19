#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class pip_installer_cli_args(object):

  def __init__(self):
    pass
  
  def pip_installer_add_args(self, subparser):

    # pip_install
    p = subparser.add_parser('install', help = 'Install pip to a new root dir.')
    self.__pip_installer_add_common_args(p)
    p.add_argument('pip_version', action = 'store', type = str, default = None,
                   help = 'The pip version [ None ]')
    p.add_argument('--clobber', action = 'store_true', default = False,
                   dest = 'clobber_install_dir',
                   help = 'Clobber the install dir if it exists [ None ]')
    
    # pip_update
    p = subparser.add_parser('update', help = 'Update pip to a specific version or install it if needed.')
    self.__pip_installer_add_common_args(p)
    p.add_argument('pip_version', action = 'store', type = str, default = None,
                   help = 'The pip version [ None ]')

    # pip_uninstall
    p = subparser.add_parser('uninstall', help = 'Uninstall pip.')
    self.__pip_installer_add_common_args(p)

  def __pip_installer_add_common_args(self, p):
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('-r', '--root-dir', action = 'store', default = None,
                   help = 'The root directory where to install pip [ None ]')
    p.add_argument('-p', '--python', action = 'store', default = None,
                   dest = 'python_exe',
                   help = 'The python executable to use [ None ]')
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The name for this pip installation [ None ]')
     
  def _command_pip_installer(self, command, *args, **kargs):
    from .pip_installer_cli_handler import pip_installer_cli_handler
    return pip_installer_cli_handler(kargs).handle_command(command)
