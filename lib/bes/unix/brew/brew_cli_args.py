#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class brew_cli_args(object):

  def __init__(self):
    pass
  
  def brew_add_args(self, subparser):

    # info
    p = subparser.add_parser('info', help = 'Print the brew version.')
    self.__brew_add_common_args(p)

    # installed
    p = subparser.add_parser('installed', help = 'Print list of installed packages.')
    self.__brew_add_common_args(p)

    # needs_update
    p = subparser.add_parser('needs_update', help = 'Check if a pacakge needs update.')
    self.__brew_add_common_args(p)
    p.add_argument('package_name', action = 'store', default = None,
                   help = 'The package to check for update []')

    # outdated
    p = subparser.add_parser('outdated', help = 'Print outdated packages.')
    self.__brew_add_common_args(p)
    
    # available
    p = subparser.add_parser('available', help = 'Print list of available packages.')

    # files
    p = subparser.add_parser('files', help = 'Print files for a package.')
    self.__brew_add_common_args(p)
    p.add_argument('-i', '--inode', action = 'store_true', default = False,
                   dest = 'print_inode',
                   help = 'Print inode for each file [ False ]')
    p.add_argument('package_name', action = 'store', default = None,
                   help = 'The package to print files for []')
    
    # install
    p = subparser.add_parser('install', help = 'Install a package.')
    self.__brew_add_common_args(p)
    p.add_argument('package_name', action = 'store', default = None,
                   help = 'The package to install []')

    # uninstall
    p = subparser.add_parser('uninstall', help = 'Uninstall a package.')
    self.__brew_add_common_args(p)
    p.add_argument('package_name', action = 'store', default = None,
                   help = 'The package to uninstall []')
    
    # files
    p = subparser.add_parser('upgrade', help = 'Upgrade a package.')
    self.__brew_add_common_args(p)
    p.add_argument('package_name', action = 'store', default = None,
                   help = 'The package to upgrade []')

    
  def __brew_add_common_args(self, p):
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')

  def _command_brew(self, command, *args, **kargs):
    from .brew_cli_handler import brew_cli_handler
    return brew_cli_handler(kargs).handle_command(command)
