#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import time

from .check import check
from .system_error import system_error

def poll_until(predicate, timeout_s, interval_s = 1.0, timeout_message = None):
  '''
  Calls predicate() repeatedly until it returns a truthy value, or
  timeout_s seconds elapse -- the shared shape behind "wait for a VM to
  report an IP", "wait for a server to open its port", etc. predicate()
  is always called at least once, even if timeout_s <= 0. Returns the
  truthy value predicate() returned. Raises system_error(timeout_message)
  if timeout_s elapses without a truthy result; a caller-specific message
  is strongly recommended since the default is generic.
  '''
  check.check_callable(predicate)
  check.check_number(timeout_s)
  check.check_number(interval_s)
  check.check_string(timeout_message, allow_none = True)

  deadline = time.monotonic() + timeout_s
  while True:
    result = predicate()
    if result:
      return result
    if time.monotonic() >= deadline:
      raise system_error(timeout_message or f'timed out after {timeout_s}s waiting for {predicate!r}')
    time.sleep(interval_s)
