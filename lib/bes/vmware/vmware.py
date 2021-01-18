#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.log import logger
from bes.system.command_line import command_line
from bes.common.check import check
from bes.fs.file_find import file_find

from .vmware_error import vmware_error
from .vmware_preferences import vmware_preferences
from .vmware_local_vm import vmware_local_vm
from .vmware_session import vmware_session
from .vmware_vmrun_exe import vmware_vmrun_exe

class vmware(object):

  logger = logger('vmware')
  
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

  def run_program(self, vm_id, username, password, program):
    vmx_filename = self._resolve_vmx_filename(vm_id)
    program_args = command_line.parse_args(program)
    args = [
      '-T', 'ws',
      '-gu', username,
      '-gp', password,
      'runProgramInGuest',
      vmx_filename,
      '-interactive',
    ] + program_args
    rv = vmware_vmrun_exe.call_vmrun(args)
    return rv
      
  def _resolve_vmx_filename(self, vm_id):
    return self._resolve_vmx_filename_local_vms(vm_id) or self._resolve_vmx_filename_rest_vms(vm_id)
  
  def _resolve_vmx_filename_local_vms(self, vm_id):
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
