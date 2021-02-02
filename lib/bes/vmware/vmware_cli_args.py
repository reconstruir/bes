#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class vmware_cli_args(object):

  def __init__(self):
    pass
  
  def vmware_add_args(self, subparser):
    
    # vm_run_program
    p = subparser.add_parser('vm_run_program', help = 'Run a program in a vm.')
    p.add_argument('--copy', action = 'store_true', default = False,
                   dest = 'copy_vm',
                   help = 'Run the program in a copy of the vm [ False ]')
    p.add_argument('--dont-ensure', action = 'store_true', default = False,
                   dest = 'dont_ensure',
                   help = 'Dont ensure that both vmware and the vm are running [ False ]')
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('username', action = 'store', type = str, default = None,
                   help = 'VM username [ ]')
    p.add_argument('password', action = 'store', type = str, default = None,
                   help = 'VM username password [ ]')
    p.add_argument('program', action = 'store', default = [], nargs = '*',
                   help = 'The program and optional arguments [ ]')

    # vm_clone
    p = subparser.add_parser('vm_clone', help = 'Clone a vm.')
    p.add_argument('--snapshot', action = 'store', type = str, default = None,
                   dest = 'snapshot_name',
                   help = 'The snapshot name []')
    p.add_argument('--clone-name', action = 'store', type = str, default = None,
                   help = 'The clone name []')
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('dst_vmx_filename', action = 'store', type = str, default = None,
                   help = 'The destination vm vmx filename [ ]')
    
  def _command_vmware(self, command, *args, **kargs):
    from .vmware_cli_handler import vmware_cli_handler
    return vmware_cli_handler(kargs).handle_command(command)
