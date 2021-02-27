#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class vmware_cli_args(object):

  def __init__(self):
    pass

  def vmware_add_args(self, subparser):

    from vmware_options_cli_args import vmware_options_cli_args
    
    # vm_run_program
    p = subparser.add_parser('vm_run_program', help = 'Run a program in a vm.')
    vmware_options_cli_args.add_arguments(p)
    self.__vmware_add_common_run_program_args(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('program', action = 'store', default = None,
                   help = 'The program [ ]')
    p.add_argument('program_args', action = 'store', default = [], nargs = '*',
                   help = 'Optional program arguments [ ]')

    # vm_run_script
    p = subparser.add_parser('vm_run_script', help = 'Run a script in a vm.')
    vmware_options_cli_args.add_arguments(p)
    self.__vmware_add_common_run_program_args(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('--interpreter', action = 'store', default = None,
                   dest = 'interpreter_name',
                   help = 'The name of the interpreter [ ]')
    p.add_argument('--file', action = 'store_true', default = False,
                   dest = 'script_is_file',
                   help = 'Use script as a filename instead of script text [ ]')
    p.add_argument('script', action = 'store', default = None,
                   help = 'The script text [ ]')
    
    # vm_run_package
    p = subparser.add_parser('vm_run_package', help = 'Run a package in a vm.')
    vmware_options_cli_args.add_arguments(p)
    self.__vmware_add_common_run_program_args(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('package_dir', action = 'store', default = None,
                   help = 'The package source dir [ ]')
    p.add_argument('entry_command', action = 'store', default = None,
                   help = 'The entry command [ ]')
    p.add_argument('entry_command_args', action = 'store', default = [], nargs = '*',
                   help = 'Optional entry command args [ ]')
    
    # vm_clone
    p = subparser.add_parser('vm_clone', help = 'Clone a vm.')
    vmware_options_cli_args.add_arguments(p)
    p.add_argument('--name', action = 'store', type = str, default = None,
                   dest = 'clone_name',
                   help = 'The clone name []')
    p.add_argument('--where', action = 'store', default = None,
                   help = 'Where to store the cloned vm files []')
    p.add_argument('--full', action = 'store_true', default = False,
                   help = 'Whether to do full instead of linked clone []')
    p.add_argument('--snapshot', action = 'store', type = str, default = None,
                   dest = 'snapshot_name',
                   help = 'The snapshot name []')
    p.add_argument('--shutdown', action = 'store_true', default = False,
                   help = 'Whether to shutdown the source vm first []')
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')

    # vm_file_copy_to
    p = subparser.add_parser('vm_file_copy_to', help = 'Copy a local file to a vm.')
    vmware_options_cli_args.add_arguments(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('local_filename', action = 'store', type = str, default = None,
                   help = 'The local filename [ ]')
    p.add_argument('remote_filename', action = 'store', type = str, default = None,
                   help = 'The remote filename [ ]')

    # vm_file_copy_from
    p = subparser.add_parser('vm_file_copy_from', help = 'Copy a remote vm file to a local file.')
    vmware_options_cli_args.add_arguments(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('remote_filename', action = 'store', type = str, default = None,
                   help = 'The remote filename [ ]')
    p.add_argument('local_filename', action = 'store', type = str, default = None,
                   help = 'The local filename [ ]')

    # vm_set_power
    from .vmware_power import vmware_power
    p = subparser.add_parser('vm_set_power_state', help = 'Get or set the vm power.')
    vmware_options_cli_args.add_arguments(p)
    p.add_argument('--wait', action = 'store_true', default = False,
                   help = 'Wait until the vm can run programs [ False ]')
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('state', action = 'store', type = str, default = None, nargs = '?',
                   choices = vmware_power.STATES,
                   help = 'The new power state [ ]')

    # vm_command
    p = subparser.add_parser('vm_command', help = 'Run a generic vmrun command that take a vmx file as its first argument.')
    vmware_options_cli_args.add_arguments(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('command', action = 'store', default = None,
                   help = 'vmrun command that take a vmx file as its first argument [ ]')
    p.add_argument('command_args', action = 'store', default = [], nargs = '*',
                   help = 'Optional command args [ ]')

    # vm_delete
    p = subparser.add_parser('vm_delete', help = 'Delete a vm.')
    vmware_options_cli_args.add_arguments(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('--shutdown', action = 'store_true', default = False,
                   help = 'Whether to shutdown the source vm first []')

    # vm_can_run_programs
    p = subparser.add_parser('vm_can_run_programs', help = 'Return 0 if the vm can run programs otherwise 1.')
    vmware_options_cli_args.add_arguments(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    
  def __vmware_add_common_run_program_args(self, p):
    'Add argument common to all commands that run programs and scripts'
    p.add_argument('--interactive', action = 'store_true', default = False,
                   help = 'Ensure a user is logged in [ False ]')
    p.add_argument('--no-wait', action = 'store_true', default = False,
                   help = 'Do not wait for the program to finish.  Return right away [ False ]')
    p.add_argument('--active-window', action = 'store_true', default = False,
                   help = 'Ensure the Windows GUI is visible.  No effect on Linux or Macos. [ False ]')
    p.add_argument('--tail-log', action = 'store_true', default = False,
                   help = 'Tail the log [ False ]')
    p.add_argument('-o', '--output', action = 'store', default = None,
                   dest = 'output_filename',
                   help = 'Output the log to filename instead of stdout [ False ]')
    
  def _command_vmware(self, __bes_command__, *args, **kargs):
    from .vmware_cli_handler import vmware_cli_handler
    return vmware_cli_handler(kargs).handle_command(__bes_command__)
