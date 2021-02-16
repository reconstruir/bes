#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class vmware_cli_args(object):

  def __init__(self):
    pass
  
  def vmware_add_args(self, subparser):
    
    # vm_run_program
    p = subparser.add_parser('vm_run_program', help = 'Run a program in a vm.')
    p.add_argument('--clone-vm', action = 'store_true', default = False,
                   help = 'Run the program in a clone of the vm [ False ]')
    p.add_argument('--interactive', action = 'store_true', default = False,
                   help = 'Run the program in interactive mode [ False ]')
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

    # vm_run_package
    p = subparser.add_parser('vm_run_package', help = 'Run a package in a vm.')
    p.add_argument('--debug', action = 'store_true', default = False,
                   help = 'Debug mode [ False ]')
    p.add_argument('--tty', action = 'store', default = None,
                   help = 'tty to log to in debug mode [ False ]')
    p.add_argument('--dont-ensure', action = 'store_true', default = False,
                   dest = 'dont_ensure',
                   help = 'Dont ensure that both vmware and the vm are running [ False ]')
    p.add_argument('--clone-vm', action = 'store_true', default = False,
                   help = 'Run the package in a clone of the vm [ False ]')
    p.add_argument('--interactive', action = 'store_true', default = False,
                   help = 'Run the program in interactive mode [ False ]')
    p.add_argument('--tail-log', action = 'store_true', default = False,
                   help = 'Tail the log [ False ]')
    p.add_argument('-o', '--output', action = 'store', default = None,
                   dest = 'output_filename',
                   help = 'Output the log to filename instead of stdout [ False ]')
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('username', action = 'store', type = str, default = None,
                   help = 'VM username [ ]')
    p.add_argument('password', action = 'store', type = str, default = None,
                   help = 'VM username password [ ]')
    p.add_argument('package_dir', action = 'store', default = None,
                   help = 'The package source dir [ ]')
    p.add_argument('entry_command', action = 'store', default = None,
                   help = 'The entry command [ ]')
    p.add_argument('entry_command_args', action = 'store', default = [], nargs = '*',
                   help = 'Optional entry command args [ ]')
    
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

    # vm_copy_to
    p = subparser.add_parser('vm_copy_to', help = 'Copy a local file to a vm.')
    p.add_argument('--dont-ensure', action = 'store_true', default = False,
                   dest = 'dont_ensure',
                   help = 'Dont ensure that both vmware and the vm are running [ False ]')
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('username', action = 'store', type = str, default = None,
                   help = 'VM username [ ]')
    p.add_argument('password', action = 'store', type = str, default = None,
                   help = 'VM username password [ ]')
    p.add_argument('local_filename', action = 'store', type = str, default = None,
                   help = 'The local filename [ ]')
    p.add_argument('remote_filename', action = 'store', type = str, default = None,
                   help = 'The remote filename [ ]')

    # vm_copy_from
    p = subparser.add_parser('vm_copy_from', help = 'Copy a remote vm file to a local file.')
    p.add_argument('--dont-ensure', action = 'store_true', default = False,
                   dest = 'dont_ensure',
                   help = 'Dont ensure that both vmware and the vm are running [ False ]')
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('username', action = 'store', type = str, default = None,
                   help = 'VM username [ ]')
    p.add_argument('password', action = 'store', type = str, default = None,
                   help = 'VM username password [ ]')
    p.add_argument('remote_filename', action = 'store', type = str, default = None,
                   help = 'The remote filename [ ]')
    p.add_argument('local_filename', action = 'store', type = str, default = None,
                   help = 'The local filename [ ]')

    # vm_set_power
    p = subparser.add_parser('vm_set_power', help = 'Get or set the vm power.')
    p.add_argument('--wait', action = 'store', default = None,
                   choices = ( 'ip', 'login', 'ssh', 'none' ),
                   help = 'Wait until the ip address is known or ssh server is up [ none ]')
    p.add_argument('--username', action = 'store', type = str, default = None,
                   help = 'VM username [ ]')
    p.add_argument('--password', action = 'store', type = str, default = None,
                   help = 'VM username password [ ]')
    p.add_argument('-n', '--num-tries', action = 'store', type = int, default = 10,
                   help = 'Number of tries for waits [ ]')
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('state', action = 'store', type = str, default = None, nargs = '?',
                   choices = ( 'on', 'off', 'shutdown', 'suspend', 'pause', 'unpause' ),
                   help = 'The new power state [ ]')
    
  def _command_vmware(self, command, *args, **kargs):
    from .vmware_cli_handler import vmware_cli_handler
    return vmware_cli_handler(kargs).handle_command(command)
