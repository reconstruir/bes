#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from os import path
import time

from ..system.check import check
from bes.fs.file_find import file_find
from bes.property.cached_property import cached_property
from bes.system.log import logger

from .bat_vmware_app import bat_vmware_app
from .bat_vmware_clone_util import bat_vmware_clone_util
from .bat_vmware_command_interpreter_manager import bat_vmware_command_interpreter_manager
from .bat_vmware_error import bat_vmware_error
from .bat_vmware_inventory import bat_vmware_inventory
from .bat_vmware_run_program_options import bat_vmware_run_program_options
from .bat_vmware_vmx_file import bat_vmware_vmx_file

class bat_vmware_local_vm(object):

  _log = logger('bat_vmware_local_vm')
  
  def __init__(self, runner, vmx_filename, login_credentials):
    check.check_bat_vmware_vmrun(runner)
    check.check_string(vmx_filename)
    check.check_credentials(login_credentials)

    self._runner = runner
    self.vmx_filename = path.abspath(vmx_filename)
    self.vmx = bat_vmware_vmx_file(self.vmx_filename)
    self.login_credentials = login_credentials
    
  def __str__(self):
    return self.vmx_filename

  def __repr__(self):
    return self.vmx_filename
  
  @cached_property
  def nickname(self):
    return self.vmx.nickname

  @cached_property
  def uuid(self):
    return self.vmx.uuid

  @property
  def is_running(self):
    return self._runner.vm_is_running(self.vmx_filename)

  @property
  def ip_address(self):
    return self._runner.vm_get_ip_address(self.vmx_filename)

  @property
  def snapshots(self):
    return self._runner.vm_snapshots(self.vmx_filename)

  @cached_property
  def system(self):
    return self.vmx.system
  
  @cached_property
  def system_info(self):
    return self.vmx.system_info

  @property
  def display_name(self):
    return self.vmx.display_name

  @property
  def interpreter(self):
    return self.vmx.interpreter

  _clone_names = namedtuple('_clone_names', 'clone_name, snapshot_name')
  def make_clone_names(self):
    timestamp = bat_vmware_clone_util.timestamp()
    clone_name = '{}_clone_{}'.format(self.nickname, timestamp)
    snapshot_name = 'snapshot_{}'.format(timestamp)
    return self._clone_names(clone_name, snapshot_name)
  
  def stop(self):
    if not self.is_running:
      return
    self._runner.vm_set_power_state(self.vmx_filename, 'stop')

  def start(self, wait = False, gui = False, run_program_options = None):
    if not self.is_running:
      self._runner.vm_set_power_state(self.vmx_filename, 'start', gui = gui)
    if wait:
      self.wait_for_can_run_programs(run_program_options = run_program_options)
    
  def can_run_programs(self, run_program_options = None):
    'Return True if the vm can run programs'
    check.check_bat_vmware_run_program_options(run_program_options, allow_none = True)

    self._log.log_method_d()
    if not self.is_running:
      return False

    if not self.ip_address:
      return False
    
    # "exit 0" works on all the default interpreters for both windows and unix
    script = 'exit 0'
    rv = self.run_script(script,
                         run_program_options = run_program_options,
                         interpreter_name = None)
    return rv.exit_code == 0

  def wait_for_can_run_programs(self, run_program_options = None):
    check.check_bat_vmware_run_program_options(run_program_options, allow_none = True)
    run_program_options = run_program_options or bat_vmware_run_program_options()

    self._log.log_method_d()
    
    num_tries = run_program_options.wait_programs_num_tries
    sleep_time = run_program_options.wait_programs_sleep_time
    self._log.log_d('wait_for_can_run_programs: num_tries={} sleep_time={}'.format(num_tries,
                                                                                      sleep_time))
    for i in range(1, num_tries + 1):
      self._log.log_d('wait_for_can_run_programs: try {} of {}'.format(i, num_tries))
      if self.can_run_programs(run_program_options = run_program_options):
        self._log.log_d('wait_for_can_run_programs: try {} success'.format(i))
        return
      self._log.log_d('wait_for_can_run_programs: sleeping for {} seconds'.format(sleep_time))
      time.sleep(sleep_time)
    self._log.log_d('wait_for_can_run_programs: timed out waiting for vm to be able to run programs.')
    raise bat_vmware_error('wait_for_can_run_programs: timed out waiting for vm to be able to run programs.')
  
  def run_script(self,
                 script,
                 run_program_options = None,
                 interpreter_name = None):
    'Return True if the vm can run programs'
    check.check_string(script)
    check.check_bat_vmware_run_program_options(run_program_options, allow_none = True)
    check.check_string(interpreter_name, allow_none = True)

    run_program_options = run_program_options or bat_vmware_run_program_options()

    self._log.log_method_d()
    
    if not self.ip_address:
      raise bat_vmware_error('vm not running: {}'.format(self.nickname))
  
    cim = bat_vmware_command_interpreter_manager.instance()
    interpreter = cim.resolve_interpreter(self.system, interpreter_name)
    self._log.log_d('run_script: interpreter={}'.format(interpreter))
    command = interpreter.build_command(script)
    self._log.log_d('run_script: command={}'.format(command))

    rv = self._runner.vm_run_script(self.vmx_filename,
                                    command.interpreter_path,
                                    command.script_text,
                                    run_program_options,
                                    self.login_credentials)
    self._log.log_d('run_script: exit_code={}'.format(rv.exit_code))
    return rv

  def run_program(self, program, program_args, run_program_options = None):
    'Return True if the vm can run programs'
    check.check_string(program)
    check.check_string_seq(program_args)
    check.check_bat_vmware_run_program_options(run_program_options, allow_none = True)

    run_program_options = run_program_options or bat_vmware_run_program_options()

    self._log.log_method_d()
    
    if not self.ip_address:
      raise bat_vmware_error('vm not running: {}'.format(self.nickname))
  
    rv = self._runner.vm_run_program(self.vmx_filename,
                                     program,
                                     program_args,
                                     run_program_options,
                                     self.login_credentials)
    self._log.log_d('run_program: exit_code={}'.format(rv.exit_code))
    return rv
  
  def clone(self, clone_name, where = None, full = False,
            snapshot_name = None, stop = False):
    check.check_string(clone_name)
    check.check_string(where, allow_none = True)
    check.check_bool(full)
    check.check_string(snapshot_name, allow_none = True)
    check.check_bool(stop)

    self._log.log_method_d()

    dst_vmx_filename = bat_vmware_clone_util.make_dst_vmx_filename(self.vmx_filename,
                                                               clone_name,
                                                               where)
    self._log.log_d('clone: dst_vmx_filename={}'.format(dst_vmx_filename))
    if path.exists(dst_vmx_filename):
      raise bat_vmware_error('Cloned vm already exists: "{}"'.format(dst_vmx_filename))

    if stop:
      self.stop()
      
    self._runner.vm_clone(self.vmx_filename,
                          dst_vmx_filename,
                          full = full,
                          snapshot_name = snapshot_name,
                          clone_name = clone_name)
    return bat_vmware_local_vm(self._runner,
                           dst_vmx_filename,
                           self.login_credentials)

  def snapshot(self, snapshot_name):
    self._log.log_method_d()
    self._runner.vm_snapshot_create(self.vmx_filename, snapshot_name)
  
  def snapshot_and_clone(self, where = None, full = False, stop = False):
    check.check_string(where, allow_none = True)
    check.check_bool(full)
    check.check_bool(stop)

    self._log.log_method_d()
    clone_name, snapshot_name = self.make_clone_names()
    self._log.log_d('snapshot_and_clone: clone_name={} snapshot_name={}'.format(clone_name,
                                                                                snapshot_name))
    self.stop()
    self.snapshot(snapshot_name)
    return self.clone(clone_name,
                      where = where,
                      full = full,
                      snapshot_name = snapshot_name,
                      stop = stop)

  def delete(self, stop = False, shutdown = False):
    check.check_bool(stop)
    check.check_bool(shutdown)

    self._log.log_method_d()

    if stop:
      self.stop()
    else:
      if self.is_running:
        raise bat_vmware_error('cannot delete a running vm: "{}"'.format(self.vmx_filename))
    if shutdown:
      bat_vmware_app.ensure_stopped()
    self._runner.vm_delete(self.vmx_filename)
    inventory_filename = bat_vmware_inventory.default_inventory_filename()
    inventory = bat_vmware_inventory(inventory_filename)
    inventory.remove_missing_vms()
    if shutdown:
      bat_vmware_app.ensure_running()

  def dir_create(self, remote_dir):
    check.check_string(remote_dir)

    self._log.log_method_d()
    self._runner.vm_dir_create(self.vmx_filename,
                               remote_dir,
                               self.login_credentials)

  def dir_delete(self, remote_dir):
    check.check_string(remote_dir)

    self._log.log_method_d()
    self._runner.vm_dir_delete(self.vmx_filename,
                               remote_dir,
                               self.login_credentials)

  def dir_list(self, remote_dir):
    check.check_string(remote_dir)

    self._log.log_method_d()
    return self._runner.vm_dir_list(self.vmx_filename,
                                    remote_dir,
                                    self.login_credentials)
    
  def file_copy_to(self, local_filename, remote_filename):
    check.check_string(local_filename)
    check.check_string(remote_filename)

    self._log.log_method_d()
    self._runner.vm_file_copy_to(self.vmx_filename,
                                 local_filename,
                                 remote_filename,
                                 self.login_credentials)

  def file_copy_from(self, remote_filename, local_filename):
    check.check_string(remote_filename)
    check.check_string(local_filename)

    self._log.log_method_d()
    self._runner.vm_file_copy_from(self.vmx_filename,
                                   remote_filename,
                                   local_filename,
                                   self.login_credentials)
    
  _info = namedtuple('_info', 'nickname, display_name, vmx_filename, interpreter, ip_address, is_running, can_run_programs, system, system_arch, system_distro, system_family, system_version, uuid')

  @property
  def info(self):
    return self._info(self.nickname,
                      self.display_name,
                      self.vmx_filename.replace(path.expanduser('~'), '~'),
                      self.interpreter,
                      self.ip_address,
                      self.is_running,
                      self.can_run_programs(),
                      self.system_info.system,
                      self.system_info.arch,
                      self.system_info.distro or '',
                      self.system_info.family or '',
                      self.system_info.version,
                      self.uuid)
  
check.register_class(bat_vmware_local_vm)
