#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path
import multiprocessing
import socket
import sys
import time
import tempfile
import inspect

from bes.archive.archiver import archiver
from ..system.check import check
from bes.common.string_util import string_util
from bes.common.table import table
from bes.common.time_util import time_util
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.system.command_line import command_line
from bes.system.host import host
from bes.system.log import logger
from bes.text.text_table import text_table

from .bat_vmware_app import bat_vmware_app
from .vmware_command_interpreter_manager import vmware_command_interpreter_manager
from .vmware_error import vmware_error
from .vmware_guest_scripts import vmware_guest_scripts
from .vmware_local_vm import vmware_local_vm
from .bat_vmware_options import bat_vmware_options
from .vmware_power import vmware_power
from .vmware_preferences import vmware_preferences
from .vmware_run_program_options import vmware_run_program_options
from .bat_vmware_restore_vm_running_state import bat_vmware_restore_vm_running_state
from .vmware_session import vmware_session
from .bat_vmware_vm import bat_vmware_vm
from .bat_vmware_vmrun import bat_vmware_vmrun
from .bat_vmware_vmx_file import bat_vmware_vmx_file
from .vmware_run_operation import vmware_run_operation

class vmware(object):

  _log = logger('vmware')
  
  def __init__(self, options = None):
    self._options = options or bat_vmware_options()
    preferences_filename = vmware_preferences.default_preferences_filename()
    self._preferences = vmware_preferences(preferences_filename)
    self._vm_dir = self._options.vm_dir or self._default_vm_dir()
    if not self._vm_dir:
      raise vmware_error('no vm_dir given in options and no default configured in {}'.format(preferences_filename))
    self._session = None
    self._runner = bat_vmware_vmrun(self._options)
    self._command_interpreter_manager = vmware_command_interpreter_manager.instance()

  @property
  def local_vms(self):
    local_vms = {}
    vmx_files = file_find.find(self._vm_dir, relative = False, match_patterns = [ '*.vmx' ])
    for vmx_filename in vmx_files:
      nickname = bat_vmware_vmx_file(vmx_filename).nickname
      login_credentials = self._options.resolve_login_credentials(nickname)
      local_vm = vmware_local_vm(self._runner, vmx_filename, login_credentials)
      local_vms[vmx_filename] = local_vm
    return local_vms
    
  def _default_vm_dir(self):
    if self._preferences.has_value('prefvmx.defaultVMPath'):
      return self._preferences.get_value('prefvmx.defaultVMPath')
    return None

  @property
  def session(self):
    if not self._session:
      self._log.log_d('session: creating session')
      self._session = vmware_session(port = self._options.vmrest_port,
                                     credentials = self._options.vmrest_credentials)
      self._log.log_d('session: starting session')
      self._session.start()
      self._log.log_d('session: starting session done')
    return self._session

  def vm_run_program(self, vm_id, program, program_args, run_program_options):
    check.check_string(vm_id)
    check.check_string(program)
    check.check_string_seq(program_args, allow_none = True)
    check.check_vmware_run_program_options(run_program_options)

    self._log.log_method_d()
    
    bat_vmware_app.ensure_running()
    vm = self._resolve_vmx_to_local_vm(vm_id)

    with bat_vmware_restore_vm_running_state(self) as _:
      with vmware_run_operation(vm, run_program_options) as target_vm:
        return target_vm.run_program(program, program_args,
                                     run_program_options = run_program_options)
      
  def vm_run_script(self, vm_id, script_text, run_program_options,
                    interpreter_name = None, script_is_file = False):
    check.check_string(vm_id)
    check.check_string(script_text)
    check.check_vmware_run_program_options(run_program_options)
    check.check_string(interpreter_name, allow_none = True)

    self._log.log_method_d()

    bat_vmware_app.ensure_running()
    vm = self._resolve_vmx_to_local_vm(vm_id)

    with bat_vmware_restore_vm_running_state(self) as _:
      with vmware_run_operation(vm, run_program_options) as target_vm:
        return target_vm.run_script(script_text,
                                    run_program_options = run_program_options,
                                    interpreter_name = interpreter_name)
  
  def vm_run_script_file(self, vm_id, script_filename, run_program_options,
                         interpreter_name = None):
    check.check_string(vm_id)
    check.check_string(script_filename)
    check.check_vmware_run_program_options(run_program_options)
    check.check_string(interpreter_name, allow_none = True)

    self._log.log_method_d()

    if not path.exists(script_filename):
      raise vmware_error('script file not found: "{}"'.format(script_filename))
    if not path.isfile(script_filename):
      raise vmware_error('script is not a file: "{}"'.format(script_filename))
    script_text = file_util.read(script_filename, codec = 'utf8')
    return self.vm_run_script(vm_id,
                              script_text,
                              run_program_options,
                              interpreter_name = interpreter_name)
  
  @classmethod
  def _clone_timestamp(clazz):
    return time_util.timestamp(delimiter = '-', milliseconds = False)

  def _clone_vm_if_needed(self, vm_id, vmx_filename, clone_vm):
    if not clone_vm:
      return vm_id, vmx_filename
    local_vm = self.local_vms[vmx_filename]
    timestamp = self._clone_timestamp()
    clone_name = '{}_clone_{}'.format(local_vm.vmx.nickname, timestamp)
    snapshot_name = 'snapshot_{}'.format(timestamp)
    self._log.log_d('_clone_vm_if_needed: vm_id={} vmx_filename={} clone_name={} snapshot_name={}'.format(vm_id,
                                                                                                          vmx_filename,
                                                                                                          clone_name,
                                                                                                          snapshot_name))
    self._log.log_d('_clone_vm_if_needed: stopping {}'.format(vmx_filename))
    self._stop_vm_if_needed(vmx_filename)
    self._log.log_d('_clone_vm_if_needed: creating snapshot')
    self._runner.vm_snapshot_create(vmx_filename, snapshot_name)
    self._log.log_d('_clone_vm_if_needed: cloning snapshot')
    rv = self.vm_clone(vm_id, clone_name = clone_name, full = False,
                       snapshot_name = snapshot_name, stop = True)
    dst_vm_id = self._vmx_filename_to_id(rv.dst_vmx_filename)
    assert dst_vm_id
    self._log.log_d('_clone_vm_if_needed: dst_mv_id={} dst_vmx_filename={}'.format(dst_vm_id, rv.dst_vmx_filename))
    return dst_vm_id, rv.dst_vmx_filename
  
  def vm_can_run_programs(self, vm_id, run_program_options):
    check.check_string(vm_id)
    check.check_vmware_run_program_options(run_program_options)

    self._log.log_method_d()
    vm = self._resolve_vmx_to_local_vm(vm_id)
    return vm.can_run_programs(run_program_options = run_program_options)

  def vm_wait_for_can_run_programs(self, vm_id, run_program_options):
    check.check_string(vm_id)
    check.check_vmware_run_program_options(run_program_options)

    self._log.log_method_d()
    
    num_tries = run_program_options.wait_programs_num_tries
    sleep_time = run_program_options.wait_programs_sleep_time
    self._log.log_d('vm_wait_for_can_run_programs: num_tries={} sleep_time={}'.format(num_tries,
                                                                                      sleep_time))
    for i in range(1, num_tries + 1):
      self._log.log_d('vm_wait_for_can_run_programs: try {} of {}'.format(i, num_tries))
      if self.vm_can_run_programs(vm_id, run_program_options):
        self._log.log_d('vm_wait_for_can_run_programs: try {} success'.format(i))
        return
      self._log.log_d('vm_wait_for_can_run_programs: sleeping for {} seconds'.format(sleep_time))
      time.sleep(sleep_time)
    self._log.log_d('vm_wait_for_can_run_programs: timed out waiting for vm to be able to run programs.')
    raise vmware_error('vm_wait_for_can_run_programs: timed out waiting for vm to be able to run programs.')
  
  def vm_run_package(self, vm_id, package_dir, entry_command, entry_command_args, run_program_options):
    check.check_string(vm_id)
    check.check_string(package_dir)
    check.check_string(entry_command)
    check.check_string_seq(entry_command_args)
    check.check_vmware_run_program_options(run_program_options)

    self._log.log_method_d()

    vm = self._resolve_vmx_to_local_vm(vm_id)

    if not path.isdir(package_dir):
      raise vmware_error('package_dir not found or not a dir: "{}"'.format(package_dir))

    tmp_dir_local = temp_file.make_temp_dir(suffix = '-run_package.dir',
                                            delete = not self._options.debug)
    if self._options.debug:
      print('tmp_dir_local={}'.format(tmp_dir_local))

    tmp_remote_dir = path.join('/tmp', path.basename(tmp_dir_local))
    self._log.log_d('vm_run_package: tmp_remote_dir={}'.format(tmp_remote_dir))

    tmp_package = self._make_tmp_file_pair(tmp_dir_local, 'package.tar.gz')
    tmp_caller_script = self._make_tmp_file_pair(tmp_dir_local, 'caller_script.py')
    tmp_output_log = self._make_tmp_file_pair(tmp_dir_local, 'output.log')

    archiver.create(tmp_package.local, package_dir)
    file_util.save(tmp_caller_script.local,
                   content = vmware_guest_scripts.RUN_PACKAGE_CALLER,
                   mode = 0o0755)
    self._log.log_d('vm_run_package: tmp_package={}'.format(tmp_package))
    self._log.log_d('vm_run_package: tmp_caller_script={}'.format(tmp_caller_script))
    self._log.log_d('vm_run_package: tmp_output_log={}'.format(tmp_output_log))

    parsed_entry_command_args = command_line.parse_args(entry_command_args)
    debug_args = []
    if self._options.debug:
      debug_args.append('--debug')
    if self._options.tty:
      debug_args.extend([ '--tty', tty ])

    caller_args = debug_args + [
      tmp_package.remote,      
      entry_command,
      tmp_output_log.remote,      
    ] + parsed_entry_command_args
      
    with bat_vmware_restore_vm_running_state(self) as _:
      with vmware_run_operation(vm, run_program_options) as target_vm:
        target_vm.dir_create(tmp_remote_dir)
        target_vm.file_copy_to(tmp_package.local, tmp_package.remote)
        target_vm.file_copy_to(tmp_caller_script.local, tmp_caller_script.remote)
        rv = target_vm.run_program(tmp_caller_script.remote,
                                   caller_args,
                                   run_program_options = run_program_options)
        target_vm.file_copy_from(tmp_output_log.remote, tmp_output_log.local)
        target_vm.dir_delete(tmp_remote_dir)
        with file_util.open_with_default(filename = run_program_options.output_filename) as f:
          log_content = file_util.read(tmp_output_log.local, codec = 'utf-8')
          f.write(log_content)
          f.flush()
    return rv

#####    process = None
#####    if run_program_options.tail_log:
#####      assert False # not working
#####      debug_args.extend([ '--tail-log-port', str(9000) ])
#####      resolved_target_vm_id = self.session.resolve_vm_id(target_vm_id)
#####      ip_address = self.session.call_client('vm_get_ip_address', resolved_target_vm_id)
#####      print('ip_address={}'.format(ip_address))
#####
#####      def _process_main(*args, **kargs):
#####        print('_process_main: args={}'.format(args))
#####        print('_process_main: kargs={}'.format(kargs))
#####        ip_address = args[0]
#####        port = args[1]
#####        print('_process_main: ip_address={} port={}'.format(ip_address, port))
#####        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#####        address = ( ip_address, port )
#####        print('client connecting...')
#####        sock.connect(address)
#####        while True:
#####          data = sock.recv(1024)
#####          s = data.decode('utf-8')
#####          print('client got: "{}"'.format(s))
#####          if s == 'byebye':
#####            break
#####        return 0
#####      
#####      process = multiprocessing.Process(name = 'caca', target = _process_main, args = ( ip_address, 9000 ))
#####      process.daemon = True
#####      process.start()

#####    if process:
#####      print('joining process')
#####      process.join()

  _tmp_file_pair = namedtuple('_tmp_file_pair', 'local, remote')
  def _make_tmp_file_pair(self, tmp_dir_local, name):
    local = path.join(tmp_dir_local, name)
    remote = path.join('/tmp', path.basename(tmp_dir_local), name)
    return self._tmp_file_pair(local, remote)
    
  def _make_temp_tmp_filename(self, local_tmp_filename):
    tmp_basename = path.basename(local_tmp_filename)
    tmp_remote_filename = path.join('/tmp', tmp_basename)
    return tmp_remote_filename

  def vm_ensure_started(self, vm_id, wait, run_program_options = None, gui = False):
    check.check_string(vm_id)
    check.check_bool(wait)
    check.check_bool(gui)
    check.check_vmware_run_program_options(run_program_options)

    run_program_options = run_program_options or vmware_run_program_options()
    
    self._log.log_method_d()
    bat_vmware_app.ensure_running()

    vmx_filename = self._resolve_vmx_filename(vm_id)
    if not self._runner.vm_is_running(vmx_filename):
      self._runner.vm_set_power_state(vmx_filename, 'start', gui = gui)
    if wait:
      self.vm_wait_for_can_run_programs(vm_id, run_program_options)
  
  def _stop_vm_if_needed(self, vmx_filename):
    if not self._runner.vm_is_running(vmx_filename):
      return
    self._runner.vm_set_power_state(vmx_filename, 'stop')
  
  _clone_result = namedtuple('_clone_result', 'src_vm, dst_vm')
  def vm_clone(self, vm_id, clone_name, where = None, full = False,
               snapshot_name = None, stop = False):
    check.check_string(vm_id)
    check.check_string(clone_name)
    check.check_string(where, allow_none = True)
    check.check_bool(full)
    check.check_string(snapshot_name, allow_none = True)
    check.check_bool(stop)

    self._log.log_method_d()

    src_vm = self._resolve_vmx_to_local_vm(vm_id)
    dst_vm = src_vm.clone(clone_name,
                          where = where,
                          full = full,
                          snapshot_name = snapshot_name,
                          stop = stop)
    return self._clone_result(src_vm, dst_vm)

  def vm_snapshot_and_clone(self, vm_id, where = None, full = False,
                            stop = False):
    check.check_string(vm_id)
    check.check_string(where, allow_none = True)
    check.check_bool(full)
    check.check_bool(stop)

    self._log.log_method_d()

    src_vm = self._resolve_vmx_to_local_vm(vm_id)
    dst_vm = src_vm.snapshot_and_clone(where = where,
                                       full = full,
                                       stop = stop)
    return self._clone_result(src_vm, dst_vm)
  
  def vm_delete(self, vm_id, stop = False, shutdown = False):
    check.check_string(vm_id)
    check.check_bool(stop)
    check.check_bool(shutdown)

    self._log.log_method_d()
    vm = self._resolve_vmx_to_local_vm(vm_id)
    self._handle_vm_delete(vm, stop, shutdown)

  def _handle_vm_delete(self, vm, stop = False, shutdown = False):
    check.check_vmware_local_vm(vm)
    check.check_bool(stop)
    check.check_bool(shutdown)

    self._log.log_method_d()

    if stop:
      vm.stop()
    else:
      if vm.is_running:
        raise vmware_error('cannot delete a running vm: "{}"'.format(vm_id))
    if shutdown:
      running_vms = self._running_vms()
      assert vm not in running_vms
      bat_vmware_app.ensure_stopped()
    self._runner.vm_delete(vm.vmx_filename)
    if shutdown:
      bat_vmware_app.ensure_running()
      assert running_vms != None
      for next_vm in running_vms:
        next_vm.start()
        
  def _save_running_vms_state(self):
    state = []
    for _, vm in self.local_vms.items():
      if vm.is_running:
        state.append(vm)
    return state

  def _restore_running_vms_state(self, vms):
    for vm in vms:
      vm.start()
  
  def vm_is_running(self, vm_id):
    check.check_string(vm_id)

    self._log.log_method_d()
    
    vmx_filename = self._resolve_vmx_filename(vm_id)
    running = self._runner.vm_is_running(vmx_filename)
    self._log.log_d('vm_is_running: running={}'.format(running))
    return 0 if running else 1

  def vm_get_ip_address(self, vm_id):
    check.check_string(vm_id)

    self._log.log_method_d()
    
    vmx_filename = self._resolve_vmx_filename(vm_id)
    ip_address = self._runner.vm_get_ip_address(vmx_filename)
    self._log.log_d('vm_get_ip_address: ip_address={}'.format(ip_address))
    if ip_address:
      print(ip_address)
      return 0
    else:
      print('')
      return 1
  
  def _resolve_vmx_filename(self, vm_id, raise_error = True):
    vmx_filename = self._resolve_vmx_filename_local_vms(vm_id) or self._resolve_vmx_filename_rest_vms(vm_id)
    if not vmx_filename and raise_error:
      raise vmware_error('failed to resolve vmx filename for id: "{}"'.format(vm_id))
    self._log.log_d('_resolve_vmx_filename: vm_id={} vmx_filename={}'.format(vm_id, vmx_filename))
    return vmx_filename

  def _resolve_vmx_to_local_vm(self, vm_id, raise_error = True):
    vmx_filename = self._resolve_vmx_filename(vm_id, raise_error = raise_error)
    nickname = bat_vmware_vmx_file(vmx_filename).nickname
    login_credentials = self._options.resolve_login_credentials(nickname)
    return vmware_local_vm(self._runner, vmx_filename, login_credentials)
  
  def _resolve_vmx_filename_local_vms(self, vm_id):
    if bat_vmware_vmx_file.is_vmx_file(vm_id):
      return vm_id
    for _, vm in self.local_vms.items():
      if vm_id in [ vm.nickname, vm.vmx_filename ]:
        return vm.vmx_filename
    return None

  def _resolve_vmx_filename_rest_vms(self, vm_id):
    rest_vms = self.session.client.vms()
    for vm in rest_vms:
      if vm_id in [ vm.name, vm.vm_id, vm.vmx_filename ]:
        return vm.vmx_filename
    return None

  def _vmx_filename_to_id(self, vmx_filename):
    rest_vms = self.session.client.vms()
    for vm in rest_vms:
      if vmx_filename == vm.vmx_filename:
        return vm.vm_id
    return None
  
  def _authentication_args(self, username = None, password = None):
    args = [ '-T', bat_vmware_app.host_type() ]
    if username:
      args.extend([ '-gu', username ])
    if password:
      args.extend([ '-gp', password ])
    return args

  def vm_file_copy_to(self, vm_id, local_filename, remote_filename):
    check.check_string(vm_id)
    check.check_string(local_filename)
    check.check_string(remote_filename)

    self._log.log_method_d()
    
    src_vmx_filename = self._resolve_vmx_filename(vm_id)
    
    local_filename = path.abspath(local_filename)
    if not path.isfile(local_filename):
      raise vmware_error('local filename not found: "{}"'.format(local_filename))

    return self._runner.vm_file_copy_to(src_vmx_filename, local_filename, remote_filename)

  def vm_file_copy_from(self, vm_id, remote_filename, local_filename):
    check.check_string(vm_id)
    check.check_string(remote_filename)
    check.check_string(local_filename)

    self._log.log_method_d()
    
    src_vmx_filename = self._resolve_vmx_filename(vm_id)

    file_util.remove(local_filename)
    result = self._runner.vm_file_copy_from(src_vmx_filename, remote_filename, local_filename)
    assert path.isfile(local_filename)
    return result

  def vm_set_power_state(self, vm_id, state, wait, gui = False):
    check.check_string(vm_id)
    check.check_string(state)
    check.check_bool(wait)
    check.check_bool(gui)

    self._log.log_method_d()
    
    vmware_power.check_state(state)
    
    bat_vmware_app.ensure_running()

    vmx_filename = self._resolve_vmx_filename(vm_id)
    
    self._log.log_d('vm_set_power: vm_id={} state={} wait={}'.format(vm_id,
                                                                     state,
                                                                     wait))

    result = self._runner.vm_set_power_state(vmx_filename, state, gui = gui)
    if wait and state in ( 'start', 'unpause' ):
      self.vm_wait_for_can_run_programs(vm_id, vmware_run_program_options())
    return result

  def vm_start(self, vm_id, wait = False, gui = False):
    check.check_string(vm_id)
    check.check_bool(wait)
    check.check_bool(gui)

    self._log.log_method_d()
    
    bat_vmware_app.ensure_running()

    vm = self._resolve_vmx_to_local_vm(vm_id)
    vm.start(gui = gui)
    if wait:
      self.vm_wait_for_can_run_programs(vm_id, vmware_run_program_options())

  def vm_stop(self, vm_id):
    check.check_string(vm_id)

    self._log.log_method_d()
    
    bat_vmware_app.ensure_running()

    vm = self._resolve_vmx_to_local_vm(vm_id)
    vm.stop()
      
  def vm_command(self, vm_id, command, command_args):
    check.check_string(vm_id)
    check.check_string(command)
    check.check_string_seq(command_args)

    self._log.log_method_d()
    
    vmx_filename = self._resolve_vmx_filename(vm_id)
    self._log.log_d('vm_command: vm_id={} vmx_filename={} command={} command_args={}'.format(vm_id,
                                                                                             vmx_filename,
                                                                                             command,
                                                                                             command_args))
    command_args = command_args or []
    args = [ command, vmx_filename ] + command_args
    return self._runner.run(args)

  def vm_snapshot_create(self, vm_id, name):
    check.check_string(vm_id)
    check.check_string(name)

    self._log.log_method_d()
    
    vmx_filename = self._resolve_vmx_filename(vm_id)
    snapshots = self._runner.vm_snapshots(vmx_filename)
    if name in snapshots:
      raise vmware_error('snapshot "{}" already exists for {}'.format(name, vmx_filename))
    self._runner.vm_snapshot_create(vmx_filename, name)

  def vm_snapshot_delete(self, vm_id, name, delete_children = False):
    check.check_string(vm_id)
    check.check_string(name)
    check.check_bool(delete_children)

    self._log.log_method_d()
    
    vmx_filename = self._resolve_vmx_filename(vm_id)
    self._runner.vm_snapshot_delete(vmx_filename, name, delete_children)

  def vm_snapshots(self, vm_id, tree = False):
    check.check_string(vm_id)
    check.check_bool(tree)

    self._log.log_method_d()
    
    vmx_filename = self._resolve_vmx_filename(vm_id)
    snapshots = self._runner.vm_snapshots(vmx_filename, tree = tree)
    for snapshot in snapshots:
      print(snapshot)

  def vms(self, show_info, show_brief):
    check.check_bool(show_info)
    check.check_bool(show_brief)

    self._log.log_method_d()
    vms = self.local_vms.items()
    if show_info:
      data = [ self._make_vm_data(vm, show_brief) for _, vm in self.local_vms.items() ]
      data = sorted(data, key = lambda row: row[0])
      tt = text_table(data = data)
      tt.set_labels(self._INFO_LABELS)
      print(tt)
    else:
      for _, vm in self.local_vms.items():
        print(vm)

  _INFO_LABELS = ( 'NAME', 'VMX_FILENAME', 'IP_ADDRESS', 'ON', 'CAN_RUN', 'SYSTEM', 'VERSION' )
  def vm_info(self, vm_id):
    check.check_string(vm_id)

    self._log.log_method_d()
    vm = self._resolve_vmx_to_local_vm(vm_id)
    tt = text_table(data = [ self._make_vm_data(vm, False) ])
    tt.set_labels(self._INFO_LABELS)
    print(tt)

  def _make_vm_data(self, vm, show_brief):
    info = vm.info
    return (
      info.nickname,
      path.basename(info.vmx_filename) if show_brief else info.vmx_filename,
      info.ip_address,
      info.is_running,
      info.can_run_programs,
      info.system,
      info.system_version
    )
