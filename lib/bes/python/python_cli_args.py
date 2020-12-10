#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class python_cli_args(object):

  def __init__(self):
    pass
  
  def python_add_args(self, subparser):

    # python_version
    p = subparser.add_parser('ver', help = 'Print the python sys.version.')
    
    # python_path
    p = subparser.add_parser('path', help = 'Print the python sys.path.')

    # python_installed
    p = subparser.add_parser('installed', help = 'Return the full versions for all installed pythons.')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   default = False, help = 'Verbose output')
    
    # python_install
    p = subparser.add_parser('install', help = 'Install python.')
    p.add_argument('full_version', action = 'store', help = 'The full version of python to install')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   default = False, help = 'Verbose output')

    # python_uninstall
    p = subparser.add_parser('uninstall', help = 'Uninstall python.')
    p.add_argument('full_version', action = 'store', help = 'The full version of python to uninstall')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   default = False, help = 'Verbose output')

    # python_reinstall
    p = subparser.add_parser('reinstall', help = 'Reinstall python.')
    p.add_argument('full_version', action = 'store', help = 'The full version of python to reinstall')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   default = False, help = 'Verbose output')

    # python_available
    p = subparser.add_parser('available', help = 'List python versions available to install.')
    p.add_argument('-n', '--num', action = 'store', type = int, default = 3,
                   help = 'Number of versions to show for each major python version [ 3 ]')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   default = False, help = 'Verbose output')

    # python_info
    p = subparser.add_parser('info', help = 'Print information about the python executable.')
    p.add_argument('exe', action = 'store', help = 'The python executable')
    
    # python_exes
    p = subparser.add_parser('exes', help = 'Print all the pythons found in PATH.')
    p.add_argument('-i', '--info', action = 'store_true', dest = 'show_info',
                   default = False, help = 'Print info about the executable')
    
  def _command_python(self, command, *args, **kargs):
    from .python_cli_command import python_cli_command
    return python_cli_command.handle_command(command, **kargs)
  
