#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class python_installer_cli_args(object):

  def __init__(self):
    pass
  
  def python_installer_add_args(self, subparser):

    # installed
    p = subparser.add_parser('installed', help = 'Return the full versions for all installed pythons.')
    self.__python_installer_add_common_args(p)

    # is_installed
    p = subparser.add_parser('is_installedinstall', help = 'Check if python is installed.')
    self.__python_installer_add_common_args(p)
    p.add_argument('version', action = 'store', help = 'The version of python to check')
    
    # install
    p = subparser.add_parser('install', help = 'Install python.')
    self.__python_installer_add_common_args(p)
    p.add_argument('version', action = 'store', help = 'The version of python to install')

    # update
    p = subparser.add_parser('install', help = 'Update python.')
    self.__python_installer_add_common_args(p)
    p.add_argument('version', action = 'store', help = 'The version of python to update')
    
    # install_package
    p = subparser.add_parser('install_package', help = 'Install a python package file directly.')
    self.__python_installer_add_common_args(p)
    p.add_argument('package_filename', action = 'store', help = 'The package filename')
    
    # uninstall
    p = subparser.add_parser('uninstall', help = 'Uninstall python.')
    self.__python_installer_add_common_args(p)
    p.add_argument('version', action = 'store', help = 'The version of python to uninstall')

    # reinstall
    p = subparser.add_parser('reinstall', help = 'Reinstall python.')
    self.__python_installer_add_common_args(p)
    p.add_argument('version', action = 'store', help = 'The version of python to reinstall')

    # available
    p = subparser.add_parser('available', help = 'List python versions available to install.')
    self.__python_installer_add_common_args(p)
    p.add_argument('-n', '--num', action = 'store', type = int, default = 3,
                   help = 'Number of versions to show for each major python version [ 3 ]')

    # installers
    p = subparser.add_parser('installers', help = 'List all available installers.')
    self.__python_installer_add_common_args(p)

    # download
    p = subparser.add_parser('download', help = 'Download python package.')
    self.__python_installer_add_common_args(p)
    p.add_argument('full_version', action = 'store', help = 'The full version of python to download')
    p.add_argument('-o', '--output', action = 'store', default = None,
                   dest = 'output_filename',
                   help = 'Output the log to filename instead of stdout [ False ]')
    
  def __python_installer_add_common_args(self, p):
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('--installer', action = 'store', default = None, type = str,
                   dest = 'installer_name',
                   help = 'The installer to use [ False ]')
    p.add_argument('--system', action = 'store', default = None, type = str,
                   choices = ( 'linux', 'macos', 'windows' ),
                   help = 'The target system [ False ]')
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Do not do any work just print what would happen [ False ]')
    p.add_argument('--debug', action = 'store_true', default = False,
                   help = 'Debug mode.  Keep temp files and logs for debugging [ False ]')
    
  def _command_python_installer(self, command, *args, **kargs):
    from .python_installer_cli_handler import python_installer_cli_handler
    return python_installer_cli_handler(kargs).handle_command(command)
