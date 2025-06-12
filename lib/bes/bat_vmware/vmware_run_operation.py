#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class vmware_run_operation(object):

  def __init__(self, vm, run_program_options):
    self._vm = vm
    self._target_vm = None
    self._run_program_options = run_program_options

  def __getattr__(self, key):
    assert self._target_vm
    return getattr(self._target_vm, key)
    
  def __enter__(self):
    if self._run_program_options.clone_vm:
      self._vm.stop()
      self._target_vm = self._vm.snapshot_and_clone(where = None, full = False)
      self._target_vm.start(gui = True, wait = True,
                            run_program_options = self._run_program_options)
    else:
      if not self._run_program_options.dont_ensure:
        self._vm.start(gui = True,
                       wait = True,
                       run_program_options = self._run_program_options)
      self._target_vm = self._vm
    return self._target_vm

  def __exit__(self, exception_type, exception_value, traceback):
    if self._run_program_options.clone_vm:
      self._target_vm.delete(stop = True, shutdown = True)
