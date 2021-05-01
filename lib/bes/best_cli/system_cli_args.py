#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class system_cli_args(object):

  def __init__(self):
    pass

  def system_add_args(self, subparser):

    # ps
    p = subparser.add_parser('ps', help = 'List processes.')

    # lsof
    p = subparser.add_parser('lsof', help = 'List open file descriptors for a process.')
    p.add_argument('pid', action = 'store', type = int, default = None,
                   help = 'The process id [ ]')
    
  def _command_system(self, __bes_command__, *args, **kargs):
    from .system_cli_handler import system_cli_handler
    return system_cli_handler(kargs).handle_command(__bes_command__)
