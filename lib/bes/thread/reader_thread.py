#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from threading import Thread
from threading import Lock
from bes.compat.Queue import Queue
from bes.compat.Queue import Empty as QueueEmptyException

from .interruptible_select import InterruptibleSelect
from bes.system import log
from .decorators import synchronized_method

class ReaderThread(Thread):
  'A thread to read from a file descriptor using select to wait for data'

  def __init__(self, fd, callback = None):
    assert fd >= 0
    super(ReaderThread, self).__init__()
    log.add_logging(self, 'reader_thread')
    self.setName(self.bes_log_tag__)
    self._select = InterruptibleSelect(fd)
    self.response_queue = Queue()
    self._running = False
    self._running_lock = Lock()
    self.daemon = True
    self._callback = callback

  @synchronized_method('_running_lock')
  def __is_running(self):
    return self._running

  @synchronized_method('_running_lock')
  def __set_is_running(self, running):
    self._running = running

  def run(self):
    self.__set_is_running(True)

    self.log_i('ReaderThread: thread starts')

    while True:
      if not self.__is_running():
        self.log_d('ReaderThread: no longer running before select')
        break

      select_result = self._select.select(None)

      if not self.__is_running():
        self.log_d('ReaderThread: no longer running after select')
        break

      if self._select.data_available(select_result):
        response_data = self.read_data()
        if response_data:
          self.log_d('ReaderThread: got line "%s"' % (response_data))
          response = ReaderThread.Response(response_data)
          self.response_queue.put(response, block = False, timeout = None)
          if self._callback:
            self._callback(response)

    self.log_d('ReaderThread: thread ends')

  def stop(self):
    self.__set_is_running(False)
    self._select.interrupt()
    self.join()
    assert not self.isAlive()

  class Response(object):
    def __init__(self, response_data):
      self.response_data = response_data

    def __str__(self):
      return 'response_data=\"%s\"' % (self.response_data)

  def read_data(self):
    'Needs to be implemented by subclasses to read data'
    assert False, 'Implement Me'

  def wait_for_response(self, timeout):
    try:
      response = self.response_queue.get(block = True, timeout = timeout)
      self.response_queue.task_done()
      return response
    except QueueEmptyException as ex:
      return None
