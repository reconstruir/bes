#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .check import check
from .managed_process import managed_process

class managed_process_generic(managed_process):
  '''
  A generic managed_process built from plain callables -- mirrors
  system_command_generic's role for system_command: lets tests (and ad
  hoc callers) exercise the managed_process contract without writing a
  dedicated subclass.
  '''

  def __init__(self, launch_fn, poll_ready_fn, terminate_fn = None):
    # Deliberately not check.check_callable() here -- it only accepts real
    # functions/methods (types.FunctionType/types.MethodType), which would
    # reject MagicMock and other callables -- exactly what tests (this
    # class's main purpose) need to pass in.
    if not callable(launch_fn):
      raise TypeError(f'launch_fn is not callable: {launch_fn!r}')
    if not callable(poll_ready_fn):
      raise TypeError(f'poll_ready_fn is not callable: {poll_ready_fn!r}')
    if terminate_fn is not None and not callable(terminate_fn):
      raise TypeError(f'terminate_fn is not callable: {terminate_fn!r}')

    super().__init__()
    self._launch_fn = launch_fn
    self._poll_ready_fn = poll_ready_fn
    self._terminate_fn = terminate_fn

  def _launch(self):
    return self._launch_fn()

  def _poll_ready(self):
    return self._poll_ready_fn()

  def _terminate(self):
    if self._terminate_fn:
      self._terminate_fn(self._handle)

check.register_class(managed_process_generic, include_seq = False)
