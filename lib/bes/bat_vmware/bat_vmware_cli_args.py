#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class bat_vmware_cli_args(object):

  def __init__(self):
    pass

  def vmware_add_args(self, subparser):

    from .bat_vmware_options_cli_args import bat_vmware_options_cli_args
    
    # vm_run_program
    p = subparser.add_parser('vm_run_program', help = 'Run a program in a vm.')
    bat_vmware_options_cli_args.add_arguments(p)
    self.__vmware_add_common_run_program_args(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('program', action = 'store', default = None,
                   help = 'The program [ ]')
    p.add_argument('program_args', action = 'store', default = [], nargs = '*',
                   help = 'Optional program arguments [ ]')
    
    # vm_run_script
    p = subparser.add_parser('vm_run_script', help = 'Run a script in a vm.')
    bat_vmware_options_cli_args.add_arguments(p)
    self.__vmware_add_common_run_program_args(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('--interpreter', action = 'store', default = None,
                   dest = 'interpreter_name',
                   help = 'The name of the interpreter [ ]')
    p.add_argument('script_text', action = 'store', default = None,
                   help = 'The script text [ ]')

    # vm_run_script_file
    p = subparser.add_parser('vm_run_script_file', help = 'Run a script in a vm from a local file.')
    bat_vmware_options_cli_args.add_arguments(p)
    self.__vmware_add_common_run_program_args(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('--interpreter', action = 'store', default = None,
                   dest = 'interpreter_name',
                   help = 'The name of the interpreter [ ]')
    p.add_argument('script_filename', action = 'store', default = None,
                   help = 'The script filename [ ]')

    # vm_run_package
    p = subparser.add_parser('vm_run_package', help = 'Run a package in a vm.')
    bat_vmware_options_cli_args.add_arguments(p)
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
    bat_vmware_options_cli_args.add_arguments(p)
    p.add_argument('--where', action = 'store', default = None,
                   help = 'Where to store the cloned vm files []')
    p.add_argument('--full', action = 'store_true', default = False,
                   help = 'Whether to do full instead of linked clone []')
    p.add_argument('--snapshot', action = 'store', type = str, default = None,
                   dest = 'snapshot_name',
                   help = 'The snapshot name []')
    p.add_argument('--stop', action = 'store_true', default = False,
                   help = 'Whether to stop the source vm first []')
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The source vm id [ ]')
    p.add_argument('clone_name', action = 'store', type = str, default = None,
                   help = 'The clone name []')

    # vm_snapshot_and_clone
    p = subparser.add_parser('vm_snapshot_and_clone', help = 'Snapshot and clone a vm from it.')
    bat_vmware_options_cli_args.add_arguments(p)
    p.add_argument('--where', action = 'store', default = None,
                   help = 'Where to store the cloned vm files []')
    p.add_argument('--full', action = 'store_true', default = False,
                   help = 'Whether to do full instead of linked clone []')
    p.add_argument('--stop', action = 'store_true', default = False,
                   help = 'Whether to stop the source vm first []')
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm source id [ ]')
    
    # vm_file_copy_to
    p = subparser.add_parser('vm_file_copy_to', help = 'Copy a local file to a vm.')
    bat_vmware_options_cli_args.add_arguments(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('local_filename', action = 'store', type = str, default = None,
                   help = 'The local filename [ ]')
    p.add_argument('remote_filename', action = 'store', type = str, default = None,
                   help = 'The remote filename [ ]')

    # vm_file_copy_from
    p = subparser.add_parser('vm_file_copy_from', help = 'Copy a remote vm file to a local file.')
    bat_vmware_options_cli_args.add_arguments(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('remote_filename', action = 'store', type = str, default = None,
                   help = 'The remote filename [ ]')
    p.add_argument('local_filename', action = 'store', type = str, default = None,
                   help = 'The local filename [ ]')

    # vm_set_power
    from .vmware_power import vmware_power
    p = subparser.add_parser('vm_set_power_state', help = 'Get or set the vm power.')
    bat_vmware_options_cli_args.add_arguments(p)
    p.add_argument('--wait', action = 'store_true', default = False,
                   help = 'Wait until the vm can run programs [ False ]')
    p.add_argument('--gui', action = 'store_true', default = False,
                   help = 'Show the GUI [ False ]')
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('state', action = 'store', type = str, default = None, nargs = '?',
                   choices = vmware_power.STATES,
                   help = 'The new power state [ ]')

    # vm_start
    p = subparser.add_parser('vm_start', help = 'Start a vm.')
    bat_vmware_options_cli_args.add_arguments(p)
    p.add_argument('--wait', action = 'store_true', default = False,
                   help = 'Wait until the vm can run programs [ False ]')
    p.add_argument('--gui', action = 'store_true', default = False,
                   help = 'Show the GUI [ False ]')
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')

    # vm_stop
    p = subparser.add_parser('vm_stop', help = 'Stop a vm.')
    bat_vmware_options_cli_args.add_arguments(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    
    # vm_command
    p = subparser.add_parser('vm_command', help = 'Run a generic vmrun command that take a vmx file as its first argument.')
    bat_vmware_options_cli_args.add_arguments(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('command', action = 'store', default = None,
                   help = 'vmrun command that take a vmx file as its first argument [ ]')
    p.add_argument('command_args', action = 'store', default = [], nargs = '*',
                   help = 'Optional command args [ ]')

    # vm_delete
    p = subparser.add_parser('vm_delete', help = 'Delete a vm.')
    bat_vmware_options_cli_args.add_arguments(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('--stop', action = 'store_true', default = False,
                   help = 'Whether to stop the vm first if needed []')
    p.add_argument('--shutdown', action = 'store_true', default = False,
                   help = 'Whether to shutdown vmware completely to avoid flakiness []')

    # vm_can_run_programs
    p = subparser.add_parser('vm_can_run_programs', help = 'Return 0 if the vm can run programs otherwise 1.')
    bat_vmware_options_cli_args.add_arguments(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')

    # vm_is_running
    p = subparser.add_parser('vm_is_running', help = 'Return 0 if the vm is running.')
    bat_vmware_options_cli_args.add_arguments(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')

    # vm_get_ip_address
    p = subparser.add_parser('vm_get_ip_address', help = 'Return the ip address for the vm0 if the vm is runningw.')
    bat_vmware_options_cli_args.add_arguments(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')

    # vm_snapshot_create
    p = subparser.add_parser('vm_snapshot_create', help = 'Create a vm snapshot.')
    bat_vmware_options_cli_args.add_arguments(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The snapshot name []')

    # vm_snapshot_delete
    p = subparser.add_parser('vm_snapshot_delete', help = 'Delete a vm snapshot.')
    bat_vmware_options_cli_args.add_arguments(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('name', action = 'store', type = str, default = None,
                   help = 'The snapshot name []')
    p.add_argument('--delete-children', action = 'store_true', default = False,
                   help = 'Whether to delete the snapshot children as well []')

    # vm_snapshots
    p = subparser.add_parser('vm_snapshots', help = 'List snapshots for a vm.')
    bat_vmware_options_cli_args.add_arguments(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')
    p.add_argument('--tree', action = 'store_true', default = False,
                   help = 'Show as a tree []')

    # vm_info
    p = subparser.add_parser('vm_info', help = 'Print all known info about a vm.')
    bat_vmware_options_cli_args.add_arguments(p)
    p.add_argument('vm_id', action = 'store', type = str, default = None,
                   help = 'The vm id [ ]')

    # vms
    p = subparser.add_parser('vms', help = 'List vms.')
    p.add_argument('-i', '--info', action = 'store_true', default = False,
                   dest = 'show_info',
                   help = 'Show as all known info about a vm [ False ]')
    p.add_argument('-b', '--brief', action = 'store_true', default = False,
                   dest = 'show_brief',
                   help = 'Brief output [ False ]')
    bat_vmware_options_cli_args.add_arguments(p)
    
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
    p.add_argument('--wait-programs-num-tries', action = 'store', type = int, default = 60,
                   help = 'The number of tries when waiting for vm to be able to run programs [ False ]')
    p.add_argument('--wait-programs-sleep-time', action = 'store', type = float, default = 2.0,
                   help = 'Amount of time in seconds to sleep between wait for programs retries [ False ]')
    p.add_argument('--clone-vm', action = 'store_true', default = False,
                   help = 'Run programs in a clone of the vm [ False ]')
    p.add_argument('--dont-ensure', action = 'store_true', default = False,
                   dest = 'dont_ensure',
                   help = 'Do not ensure that the vm is running [ False ]')
    
  def _command_vmware(self, __bes_command__, *args, **kargs):
    from .bat_vmware_cli_handler import bat_vmware_cli_handler
    return bat_vmware_cli_handler(kargs).handle_command(__bes_command__)
