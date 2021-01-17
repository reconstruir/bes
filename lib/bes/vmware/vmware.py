#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.log import logger
from bes.common.check import check
from bes.fs.file_find import file_find

from .vmware_error import vmware_error
from .vmware_preferences import vmware_preferences
from .vmware_local_vm import vmware_local_vm

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

  def _default_vm_dir(self):
    if self._preferences.has_value('prefvmx.defaultVMPath'):
      return self._preferences.get_value('prefvmx.defaultVMPath')
    return None
