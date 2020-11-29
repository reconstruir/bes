#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class brew_installer_cli_args(object):

  def __init__(self):
    pass
  
  def brew_installer_add_args(self, subparser):

    # run_script
    p = subparser.add_parser('run_script', help = 'Download and run a brew script.')
    self.__brew_installer_add_common_args(p)
    p.add_argument('--print', action = 'store_true', default = False,
                   dest = 'print_only',
                   help = 'Print the script instead of running it [ False ]')
    p.add_argument('script_name', action = 'store', default = None,
                   help = 'The name of the script such as install.sh or uninstall.sh [ None ]')
    p.add_argument('args', action = 'store', default = None, nargs = '*',
                   help = 'Arguments for the script [ ]')

    # install
    p = subparser.add_parser('install', help = 'Install brew.')
    self.__brew_installer_add_common_args(p)

    # uninstall
    p = subparser.add_parser('uninstall', help = 'Uninstall brew.')
    self.__brew_installer_add_common_args(p)
    
    # reinstall
    p = subparser.add_parser('reinstall', help = 'Reinstall brew.')
    self.__brew_installer_add_common_args(p)

    # ensure
    p = subparser.add_parser('ensure', help = 'Ensure brew is installed.')
    self.__brew_installer_add_common_args(p)
    
  def __brew_installer_add_common_args(self, p):
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('-p', '--password', action = 'store', default = None,
                   help = 'The sudo password to use [ ]')
    
  def _command_brew_installer(self, command, *args, **kargs):
    from .brew_installer_cli_command import brew_installer_cli_command
    return brew_installer_cli_command.handle_command(command, **kargs)
