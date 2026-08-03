#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import ABCMeta, abstractmethod

from .check import check
from .poll_until import poll_until

class managed_process(object, metaclass = ABCMeta):
  '''
  Base class for a long-lived background process that must be started and
  then waited on for an external readiness signal (a VM reporting an IP, a
  server binding a port, ...), with the common start()/stop()/is_running
  machinery factored out. The launch mechanism and the readiness check are
  exactly the parts that legitimately vary per concrete process -- they're
  left to the subclass; only the "launch, then poll for readiness with a
  deadline, then expose stop()" shape is shared.

  Subclasses implement:
    _launch()     -- start the underlying process/handle; return an opaque
                     handle (this class never inspects it, only checks it
                     for None). May raise -- any exception here propagates
                     immediately out of start(), before the readiness poll
                     ever begins (e.g. a missing command).
    _poll_ready()  -- return a truthy "ready" value (whatever's useful to
                     the caller -- an address, an IP, True) once ready, or
                     a falsy value if not yet ready. Called repeatedly by
                     start() via poll_until() until truthy or timeout.
    _terminate()   -- stop the handle returned by _launch(). Called by
                     stop(); must tolerate being called on an
                     already-finished/dead process.
  '''

  def __init__(self):
    self._handle = None
    self.ready_value = None

  @abstractmethod
  def _launch(self):
    raise NotImplementedError('_launch')

  @abstractmethod
  def _poll_ready(self):
    raise NotImplementedError('_poll_ready')

  @abstractmethod
  def _terminate(self):
    raise NotImplementedError('_terminate')

  def start(self, timeout_s = 60, interval_s = 1.0):
    'Launch the process and block until _poll_ready() is truthy or timeout_s elapses.'
    check.check_number(timeout_s)
    check.check_number(interval_s)

    self._handle = self._launch()
    self.ready_value = poll_until(
      self._poll_ready,
      timeout_s = timeout_s,
      interval_s = interval_s,
      timeout_message = f'{self.__class__.__name__} did not become ready within {timeout_s}s')
    return self.ready_value

  def stop(self):
    'Terminate the process, if one was ever launched. Safe to call more than once.'
    if self._handle is None:
      return
    self._terminate()
    self._handle = None
    self.ready_value = None

  @property
  def is_running(self):
    return self._handle is not None

check.register_class(managed_process, include_seq = False)
