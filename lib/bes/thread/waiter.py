#!/usr/bin/env python
#-*- coding:utf-8 -*-

from decorators import synchronized_method
from threading import Lock
from Queue import Queue, Empty as QueueEmptyException

class Waiter(object):

  def __init__(self):
    self._lock = Lock()
    self._queue = Queue()
    self._notified = False

  def wait(self, timeout = None):
    if self.was_notified():
      return True

    try:
      self._queue.get(block = True, timeout = timeout)
      self._queue.task_done()
      return True
    except QueueEmptyException, ex:
      return False

  def notify(self):
    self._lock.acquire()
    self._notified = True
    self._lock.release()
    self._queue.put(None, block = True, timeout = None)

  @synchronized_method('_lock')
  def was_notified(self):
    return self._notified
