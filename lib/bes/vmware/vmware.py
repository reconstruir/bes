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
from bes.common.check import check
from bes.common.string_util import string_util
from bes.common.time_util import time_util
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.system.command_line import command_line
from bes.system.host import host
from bes.system.log import logger
from bes.text.text_table import text_table

from .vmware_app import vmware_app
from .vmware_command_interpreter_manager import vmware_command_interpreter_manager
from .vmware_error import vmware_error
from .vmware_guest_scripts import vmware_guest_scripts
from .vmware_local_vm import vmware_local_vm
from .vmware_options import vmware_options
from .vmware_power import vmware_power
from .vmware_preferences import vmware_preferences
from .vmware_run_program_options import vmware_run_program_options
from .vmware_session import vmware_session
from .vmware_vm import vmware_vm
from .vmware_vmrun import vmware_vmrun
from .vmware_vmx_file import vmware_vmx_file

class vmware(object):

  _log = logger('vmware')
  
  def __init__(self, options = None):
    self._options = options or vmware_options()
    self._preferences_filename = vmware_preferences.default_preferences_filename()
    self._preferences = vmware_preferences(self._preferences_filename)
    self._vm_dir = self._options.vm_dir or self._default_vm_dir()
    if not self._vm_dir:
      raise vmware_error('no vm_dir given in options and no default configured in {}'.format(self._preferences_filename))
    self._session = None
    self._runner = vmware_vmrun(login_credentials = self._options.login_credentials)
    self._command_interpreter_manager = vmware_command_interpreter_manager.instance()

  @property
  def local_vms(self):
    local_vms = {}
    vmx_files = file_find.find(self._vm_dir, relative = False, match_patterns = [ '*.vmx' ])
    for vmx_filename in vmx_files:
      local_vm = vmware_local_vm(self._runner, vmx_filename)
      local_vms[vmx_filename] = local_vm
    return local_vms
    
  def _default_vm_dir(self):
    if self._preferences.has_value('prefvmx.defaultVMPath'):
      return self._preferences.get_value('prefvmx.defaultVMPath')
    return None

  @classmethod
  def _tmp_nickname_part(clazz):
    d = tempfile.mkdtemp(prefix = 'foo')
    b = path.basename(d)
    file_util.remove(d)
    return string_util.remove_head(b, 'foo')

  _cloned_vm_names = namedtuple('_cloned_vm_names', 'src_vmx_filename, dst_vmx_filename, dst_vmx_nickname')
  def _make_cloned_vm_names(clazz, src_vmx_filename, clone_name, where):
    vms_root_dir = path.normpath(path.join(path.dirname(src_vmx_filename), path.pardir))
    src_vmx_nickname = vmware_vmx_file(src_vmx_filename).nickname
    tmp_nickname_part = clazz._tmp_nickname_part()
    if not clone_name:
      clone_name = '{}_clone_{}'.format(src_vmx_nickname, tmp_nickname_part)
    new_vm_root_dir_basename = '{}.vmwarevm'.format(clone_name)
    if not where:
      where = path.join(vms_root_dir, new_vm_root_dir_basename)
    file_util.mkdir(where)
    dst_vmx_basename = '{}.vmx'.format(clone_name)
    dst_vmx_filename = path.join(where, dst_vmx_basename)
    return clazz._cloned_vm_names(src_vmx_filename, dst_vmx_filename, clone_name)
  
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
    
    vmx_filename = self._resolve_vmx_filename(vm_id)
    target_vm_id, target_vmx_filename = self._clone_vm_if_needed(vm_id,
                                                                 vmx_filename,
                                                                 self._options.clone_vm)
    
    if not self._options.dont_ensure or self._options.clone_vm:
      self.vm_ensure_started(target_vm_id, True, run_program_options = run_program_options, gui = True)
      
    rv = self._runner.vm_run_program(target_vmx_filename, program, program_args, run_program_options)

    if self._options.clone_vm and not self._options.debug:
      self._runner.vm_stop(target_vmx_filename)
      self._runner.vm_delete(target_vmx_filename)

    return rv

  def vm_run_script(self, vm_id, script, run_program_options,
                    interpreter_name = None, script_is_file = False):
    check.check_string(vm_id)
    check.check_string(script)
    check.check_vmware_run_program_options(run_program_options)
    check.check_string(interpreter_name, allow_none = True)
    check.check_bool(script_is_file)

    self._log.log_method_d()
    vmware_app.ensure_running()

    if script_is_file:
      if not path.exists(script):
        raise vmware_error('script file not found: "{}"'.format(script))
      if not path.isfile(script):
        raise vmware_error('script is not a file: "{}"'.format(script))
      script_text = file_util.read(script, codec = 'utf8')
    else:
      script_text = script

    vmx_filename = self._resolve_vmx_filename(vm_id)
    local_vm = self.local_vms[vmx_filename]
    system = local_vm.vmx.system
    interpreter = self._command_interpreter_manager.resolve_interpreter(system, interpreter_name)
    if not interpreter:
      raise vmware_error('Failed to resolve interpreter for "{}": "{}"'.format(vm_id, interpreter))
    self._log.log_d('vm_run_script: interpreter={}'.format(interpreter))
    command = interpreter.build_command(script_text)
    self._log.log_d('vm_run_script: command={}'.format(command))
    target_vm_id, target_vmx_filename = self._clone_vm_if_needed(vm_id,
                                                                 vmx_filename,
                                                                 self._options.clone_vm)
    if not self._options.dont_ensure or self._options.clone_vm:
      self.vm_ensure_started(target_vm_id, True, run_program_options = run_program_options, gui = True)

    rv = self._runner.vm_run_script(target_vmx_filename,
                                    command.interpreter_path,
                                    command.script_text,
                                    run_program_options)

    if self._options.clone_vm and not self._options.debug:
      self._runner.vm_stop(target_vmx_filename)
      vmware_app.ensure_stopped()
      self._runner.vm_delete(target_vmx_filename)

    return rv
  
  @classmethod
  def _tmp_nickname_part(clazz):
    d = tempfile.mkdtemp()
    b = path.basename(d)
    file_util.remove(d)
    return string_util.remove_head(b, 'tmp')

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
                       snapshot_name = snapshot_name, shutdown = True)
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
    
    num_tries = self._options.wait_programs_num_tries
    sleep_time = self._options.wait_programs_sleep_time
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

    debug = self._options.debug
    
    if not path.isdir(package_dir):
      raise vmware_error('package_dir not found or not a dir: "{}"'.format(package_dir))

    vmx_filename = self._resolve_vmx_filename(vm_id)
    self._log.log_d('vm_run_package: vmx_filename={} dont_ensure={}'.format(vmx_filename,
                                                                            self._options.dont_ensure))

    target_vm_id, target_vmx_filename = self._clone_vm_if_needed(vm_id,
                                                                 vmx_filename,
                                                                 self._options.clone_vm)
    assert target_vm_id
    assert path.isfile(target_vmx_filename)
    self._log.log_d('vm_run_package: target_vm_id={} target_vmx_filename={}'.format(target_vm_id,
                                                                                    target_vmx_filename))
    
    if not self._options.dont_ensure or self._options.clone_vm:
      self.vm_ensure_started(target_vm_id, True, run_program_options = run_program_options, gui = True)
      
    tmp_dir_local = temp_file.make_temp_dir(suffix = '-run_package.dir', delete = not debug)
    if debug:
      print('tmp_dir_local={}'.format(tmp_dir_local))

    tmp_remote_dir = path.join('/tmp', path.basename(tmp_dir_local))
    self._log.log_d('vm_run_package: tmp_remote_dir={}'.format(tmp_remote_dir))

    self._runner.vm_dir_create(target_vmx_filename, tmp_remote_dir)
    
    tmp_package = self._make_tmp_file_pair(tmp_dir_local, 'package.zip')
    tmp_caller_script = self._make_tmp_file_pair(tmp_dir_local, 'caller_script.py')
    tmp_output_log = self._make_tmp_file_pair(tmp_dir_local, 'output.log')

    archiver.create(tmp_package.local, package_dir)
    file_util.save(tmp_caller_script.local,
                   content = vmware_guest_scripts.RUN_PACKAGE_CALLER,
                   mode = 0o0755)
    self._log.log_d('vm_run_package: tmp_package={}'.format(tmp_package))
    self._log.log_d('vm_run_package: tmp_caller_script={}'.format(tmp_caller_script))
    self._log.log_d('vm_run_package: tmp_output_log={}'.format(tmp_output_log))

    self._runner.vm_file_copy_to(target_vmx_filename, tmp_package.local, tmp_package.remote)
    self._runner.vm_file_copy_to(target_vmx_filename, tmp_caller_script.local, tmp_caller_script.remote)

    parsed_entry_command_args = command_line.parse_args(entry_command_args)
    debug_args = []
    if self._options.debug:
      debug_args.append('--debug')
    if self._options.tty:
      debug_args.extend([ '--tty', tty ])

    process = None
    if run_program_options.tail_log:
      assert False # not working
      debug_args.extend([ '--tail-log-port', str(9000) ])
      resolved_target_vm_id = self.session.resolve_vm_id(target_vm_id)
      ip_address = self.session.call_client('vm_get_ip_address', resolved_target_vm_id)
      print('ip_address={}'.format(ip_address))

      def _process_main(*args, **kargs):
        print('_process_main: args={}'.format(args))
        print('_process_main: kargs={}'.format(kargs))
        ip_address = args[0]
        port = args[1]
        print('_process_main: ip_address={} port={}'.format(ip_address, port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = ( ip_address, port )
        print('client connecting...')
        sock.connect(address)
        while True:
          data = sock.recv(1024)
          s = data.decode('utf-8')
          print('client got: "{}"'.format(s))
          if s == 'byebye':
            break
        return 0
      
      process = multiprocessing.Process(name = 'caca', target = _process_main, args = ( ip_address, 9000 ))
      process.daemon = True
      process.start()

    caller_args = debug_args + [
      tmp_package.remote,      
      entry_command,
      tmp_output_log.remote,      
    ] + parsed_entry_command_args
    rv = self._runner.vm_run_program(target_vmx_filename,
                                     tmp_caller_script.remote,
                                     caller_args,
                                     run_program_options)

    self._runner.vm_file_copy_from(target_vmx_filename, tmp_output_log.remote, tmp_output_log.local)

    with file_util.open_with_default(filename = run_program_options.output_filename) as f:
      log_content = file_util.read(tmp_output_log.local, codec = 'utf-8')
      f.write(log_content)

    # cleanup the tmp dir but only if debug is False
    if not debug:
      self._runner.vm_dir_delete(target_vmx_filename, tmp_remote_dir)

    if self._options.clone_vm and not self._options.debug:
      self._runner.vm_stop(target_vmx_filename)
      self._runner.vm_delete(target_vmx_filename)
      
    if process:
      print('joining process')
      process.join()
      
    return rv

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
    check.check_vmware_run_program_options(run_program_options)

    run_program_options = run_program_options or vmware_run_program_options()
    
    self._log.log_method_d()
    vmware_app.ensure_running()

    vmx_filename = self._resolve_vmx_filename(vm_id)
    if not self._runner.vm_is_running(vmx_filename):
      self._runner.vm_set_power_state(vmx_filename, 'start', gui = gui)
    if wait:
      self.vm_wait_for_can_run_programs(vm_id, run_program_options)
  
  def _stop_vm_if_needed(self, vmx_filename):
    if not self._runner.vm_is_running(vmx_filename):
      return
    self._runner.vm_set_power_state(vmx_filename, 'stop')
  
  _clone_result = namedtuple('_clone_result', 'src_vmx_filename, dst_vmx_filename')
  def vm_clone(self, vm_id, clone_name = None, where = None, full = False,
               snapshot_name = None, shutdown = False):
    check.check_string(vm_id)
    check.check_string(clone_name, allow_none = True)
    check.check_string(where, allow_none = True)
    check.check_bool(full)
    check.check_string(snapshot_name, allow_none = True)
    check.check_bool(shutdown)

    self._log.log_method_d()
    
    src_vmx_filename = self._resolve_vmx_filename(vm_id)
    self._log.log_d('vm_clone: src_vmx_filename={}'.format(src_vmx_filename))

    names = self._make_cloned_vm_names(src_vmx_filename, clone_name, where)
    self._log.log_d('vm_clone: dst_vmx_filename={} dst_vmx_nickname={}'.format(names.dst_vmx_filename,
                                                                                names.dst_vmx_nickname))
    if path.exists(names.dst_vmx_filename):
      raise vmware_error('Clones vmx file already exists: "{}"'.format(names.dst_vmx_filename))

    if shutdown:
      self._stop_vm_if_needed(src_vmx_filename)
      
    self._runner.vm_clone(src_vmx_filename,
                          names.dst_vmx_filename,
                          full = full,
                          snapshot_name = snapshot_name,
                          clone_name = names.dst_vmx_nickname)
    return self._clone_result(src_vmx_filename, names.dst_vmx_filename)

  def vm_delete(self, vm_id, shutdown = False):
    check.check_string(vm_id)
    check.check_bool(shutdown)

    self._log.log_method_d()

    vmx_filename = self._resolve_vmx_filename(vm_id)
    self._log.log_d('vm_delete: vmx_filename={}'.format(vmx_filename))
    if shutdown:
      self._stop_vm_if_needed(vmx_filename)
    self._runner.vm_delete(vmx_filename)

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
    return vmware_local_vm(self._runner, vmx_filename)
  
  def _resolve_vmx_filename_local_vms(self, vm_id):
    if vmware_vmx_file.is_vmx_file(vm_id):
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
    args = [ '-T', vmware_app.host_type() ]
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

    self._log.log_method_d()
    
    vmware_power.check_state(state)
    
    vmware_app.ensure_running()

    vmx_filename = self._resolve_vmx_filename(vm_id)
    
    self._log.log_d('vm_set_power: vm_id={} state={} wait={}'.format(vm_id,
                                                                     state,
                                                                     wait))

    result = self._runner.vm_set_power_state(vmx_filename, state, gui = gui)
    if wait and state in ( 'start', 'unpause' ):
      self.vm_wait_for_can_run_programs(vm_id, vmware_run_program_options())
    return result

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

  def vms(self, show_info):
    check.check_bool(show_info)
    
    self._log.log_method_d()
    for _, vm in self.local_vms.items():
      print(vm)

  def vm_info(self, vm_id):
    check.check_string(vm_id)

    self._log.log_method_d()

    vm = self._resolve_vmx_to_local_vm(vm_id)
    data = [
      ( 'vmx_filename', vm.vmx_filename, ),
      ( 'display_name', vm.display_name ),
      ( 'interpreter', vm.interpreter ),
      ( 'ip_address', vm.ip_address ),
      ( 'is_running', vm.is_running ),
      ( 'can_run_programs', vm.can_run_programs() ),
      ( 'nickname', vm.nickname, ),
      ( 'system arch', vm.system_info.arch ),
      ( 'system distro', vm.system_info.distro or '' ),
      ( 'system family', vm.system_info.family or '' ),
      ( 'system version', vm.system_info.version ),
      ( 'system', vm.system_info.system ),
      ( 'uuid', vm.uuid ),
    ]
    for i, snapshot in enumerate(vm.snapshots):
      data.append( ( 'snapshot {}'.format(i + 1), snapshot ) )
      
    tt = text_table(data = data)
    print(tt)
    #tt.set_labels( tuple([ f.upper() for f in vms[0]._fields ]) )
