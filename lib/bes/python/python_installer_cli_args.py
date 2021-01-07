#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class python_installer_cli_args(object):

  def __init__(self):
    pass
  
  def python_installer_add_args(self, subparser):

    # installed
    p = subparser.add_parser('installed', help = 'Return the full versions for all installed pythons.')
    self.__python_installer_add_common_args(p)

    # install
    p = subparser.add_parser('install', help = 'Install python.')
    p.add_argument('full_version', action = 'store', help = 'The full version of python to install')
    self.__python_installer_add_common_args(p)

    # uninstall
    p = subparser.add_parser('uninstall', help = 'Uninstall python.')
    p.add_argument('full_version', action = 'store', help = 'The full version of python to uninstall')
    self.__python_installer_add_common_args(p)

    # reinstall
    p = subparser.add_parser('reinstall', help = 'Reinstall python.')
    p.add_argument('full_version', action = 'store', help = 'The full version of python to reinstall')
    self.__python_installer_add_common_args(p)

    # available
    p = subparser.add_parser('available', help = 'List python versions available to install.')
    p.add_argument('-n', '--num', action = 'store', type = int, default = 3,
                   help = 'Number of versions to show for each major python version [ 3 ]')
    self.__python_installer_add_common_args(p)

  def __python_installer_add_common_args(self, p):
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('--installer', action = 'store', default = None, type = str,
                   dest = 'installer_name',
                   help = 'The installer to use [ False ]')
    
  def _command_python_installer(self, command, *args, **kargs):
    from .python_installer_cli_command import python_installer_cli_command
    return python_installer_cli_command(kargs).handle_command(command)
