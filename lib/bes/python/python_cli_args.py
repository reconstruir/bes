#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class python_cli_args(object):

  def __init__(self):
    pass
  
  def python_add_args(self, subparser):

    # python_version
    p = subparser.add_parser('ver', help = 'Print the python sys.version.')
    
    # python_path
    p = subparser.add_parser('path', help = 'Print the python sys.path.')

    # python_info
    p = subparser.add_parser('info', help = 'Print information about the python executable.')
    p.add_argument('exe', action = 'store', help = 'The python executable')
    
    # python_exes
    p = subparser.add_parser('exes', help = 'Print all the pythons found in PATH.')
    p.add_argument('-i', '--info', action = 'store_true', dest = 'show_info',
                   default = False, help = 'Print info about the executable')
    
  def _command_python(self, command, *args, **kargs):
    from .python_cli_command import python_cli_command
    return python_cli_command(kargs).handle_command(command)
