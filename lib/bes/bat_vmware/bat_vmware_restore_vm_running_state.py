#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class bat_vmware_restore_vm_running_state(object):

  def __init__(self, vmware):
    self._vmware = vmware
    self._state = None

  def __enter__(self):
    self._state = self._running_vms(self._vmware)

  def __exit__(self, exception_type, exception_value, traceback):
    assert self._state != None
    self._restore_running_vms_state(self._state)
    self._state = None

  @classmethod
  def _running_vms(clazz, vmware):
    state = []
    for _, vm in vmware.local_vms.items():
      if vm.is_running:
        state.append(vm)
    return state

  def _restore_running_vms_state(clazz, vms):
    for vm in vms:
      vm.start()
