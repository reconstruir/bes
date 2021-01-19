#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class vmware_cli_args(object):

  def __init__(self):
    pass
  
  def vmware_add_args(self, subparser):
    
    # vm_run_program
    p = subparser.add_parser('vm_run_program', help = 'Run a program in a vm.')
    p.add_argument('--copy', action = 'store', type = str, default = None,
                   help = 'Run the program in a copy of the vm [ False ]')
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('username', action = 'store', type = str, default = None,
                   help = 'VM username [ ]')
    p.add_argument('password', action = 'store', type = str, default = None,
                   help = 'VM username password [ ]')
    p.add_argument('program', action = 'store', default = [], nargs = '*',
                   help = 'The program and optional arguments [ ]')

  def _command_vmware(self, command, *args, **kargs):
    from .vmware_cli_handler import vmware_cli_handler
    return vmware_cli_handler(kargs).handle_command(command)
