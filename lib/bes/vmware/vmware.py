#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.system.log import logger
from bes.system.command_line import command_line
from bes.system.host import host
from bes.common.check import check
from bes.fs.file_find import file_find

from .vmware_app import vmware_app
from .vmware_error import vmware_error
from .vmware_local_vm import vmware_local_vm
from .vmware_preferences import vmware_preferences
from .vmware_session import vmware_session
from .vmware_vmrun_exe import vmware_vmrun_exe
from .vmware_vmx_file import vmware_vmx_file

class vmware(object):

  _log = logger('vmware')
  
  def __init__(self, vm_dir = None):
    self._preferences_filename = vmware_preferences.default_preferences_filename()
    self._preferences = vmware_preferences(self._preferences_filename)
    self._vm_dir = vm_dir
    if not self._vm_dir:
      self._vm_dir = self._default_vm_dir()
    if not self._vm_dir:
      raise vmware_error('no vm_dir given and no default configured in {}'.format(self._preferences_filename))
    self.local_vms = {}
    vmx_files = file_find.find(self._vm_dir, relative = False, match_patterns = [ '*.vmx' ])
    for vmx_filename in vmx_files:
      local_vm = vmware_local_vm(vmx_filename)
      self.local_vms[local_vm.nickname] = local_vm
    self._session = None
    self._app = vmware_app()

  def _default_vm_dir(self):
    if self._preferences.has_value('prefvmx.defaultVMPath'):
      return self._preferences.get_value('prefvmx.defaultVMPath')
    return None

  @property
  def session(self):
    if not self._session:
      self._session = vmware_session()
      self._session.start()
    return self._session

  def run_program(self, vm_id, username, password, program, copy_vm, dont_ensure):
    check.check_string(vm_id)
    check.check_string(username)
    check.check_string(password)
    check.check_string_seq(program)
    check.check_bool(copy_vm)
    check.check_bool(dont_ensure)

    vmx_filename = self._resolve_vmx_filename(vm_id)
    self._log.log_d('run_program: vm_id={} vmx_filename={}'.format(vm_id, vmx_filename))

    if not dont_ensure:
      resolved_vm_id = self.session.resolve_vm_id(vm_id)
      self._log.log_d('run_program: resolved_vm_id={}'.format(resolved_vm_id))
      self._log.log_d('run_program: ensuring vmware is running')
      self._app.ensure_running()

      #self.session.call_client('', *args, **kargs)
      
      self._log.log_d('run_program: ensuring vmware is running')
      #rest_vms = self.session.client.vms()

    program_args = command_line.parse_args(program)
    args = self._authentication_args() + [
      'runProgramInGuest',
      vmx_filename,
      '-interactive',
    ] + program_args
    self._log.log_d('run_program: args={}'.format(args))
    rv = vmware_vmrun_exe.call_vmrun(args)
    return rv

  #
  #                       full|linked
  #                       [-snapshot=Snapshot Name]
  #                       [-cloneName=Name]
  
  def vm_clone(self, vm_id, dst_vmx_filename, full = False, snapshot_name = None, clone_name = None):
    check.check_string(vm_id)
    check.check_string(dst_vmx_filename)
    check.check_bool(full)
    check.check_string(snapshot_name, allow_none = True)
    check.check_string(clone_name, allow_none = True)
    
    src_vmx_filename = self._resolve_vmx_filename(vm_id)
    if path.exists(dst_vmx_filename):
      raise vmware_error('dst_vmx_filename already exists: "{}"'.format(dst_vmx_filename))
    
    args = self._authentication_args() + [
      'clone',
      src_vmx_filename,
      dst_vmx_filename,
      'full' if full else 'linked',
    ]
    if snapshot_name:
      args.append('-snapshot="{}"'.format(snapshot_name))
    if clone_name:
      args.append('-cloneName="{}"'.format(clone_name))
    rv = vmware_vmrun_exe.call_vmrun(args)
    return rv
  
  def _resolve_vmx_filename(self, vm_id):
    return self._resolve_vmx_filename_local_vms(vm_id) or self._resolve_vmx_filename_rest_vms(vm_id)
  
  def _resolve_vmx_filename_local_vms(self, vm_id):
    if vmware_vmx_file.is_vmx_file(vm_id):
      return vm_id
    for nickname, vm in self.local_vms.items():
      if vm_id in [ nickname, vm.vmx_filename ]:
        return vm.vmx_filename
    return None

  def _resolve_vmx_filename_rest_vms(self, vm_id):
    rest_vms = self.session.client.vms()
    for vm in rest_vms:
      if vm_id == vm.vm_id:
        return vm.path
    return None

  def _authentication_args(self, username = None, password = None):
    args = [ '-T', self._app.host_type() ]
    if username:
      args.extend([ '-gu', username ])
    if password:
      args.extend([ '-gp', password ])
    return args
