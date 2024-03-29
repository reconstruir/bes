#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class python_cli_args(object):

  def __init__(self):
    pass
  
  def python_add_args(self, subparser):

    # version
    p = subparser.add_parser('ver', help = 'Print the python sys.version.')
    
    # path
    p = subparser.add_parser('path', help = 'Print the python sys.path.')

    # info
    p = subparser.add_parser('info', help = 'Print information about the python executable.')
    p.add_argument('exe', action = 'store', help = 'The python executable')
    
    # exes
    p = subparser.add_parser('exes', help = 'Print all the pythons found in PATH.')
    p.add_argument('-i', '--info', action = 'store_true', dest = 'show_info',
                   default = False, help = 'Print info about the executable')

    # default_exe
    p = subparser.add_parser('default_exe', help = 'Print the default python exe.')
    
  def _command_python(self, command, *args, **kargs):
    from .python_cli_handler import python_cli_handler
    return python_cli_handler(kargs).handle_command(command)
