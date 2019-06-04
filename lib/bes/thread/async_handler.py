#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from threading import Thread
from threading import Lock
from bes.compat.Queue import Queue
from bes.system.log import log
import pprint

class AsyncHandler(Thread):
  '''
  A class to handle data asynchronously using a thread and a queue.
  A handler will be called with the data from a separate thread.
  '''

  def __init__(self, handler):
    assert handler
    super(AsyncHandler, self).__init__()
    log.add_logging(self, 'async_handler')
    self._handler = handler
    self.setName(self.bes_log_tag__)
    self._running = False
    self._running_lock = Lock()
    self._queue = Queue()
    self.daemon = True

  def run(self):
    self._running_lock.acquire()
    self._running = True
    self._running_lock.release()

    self.log_d('AsyncHandler() starts')
    while True:
      self.log_d('calling __main_loop_iteration()')
      if not self.__main_loop_iteration():
        self.log_d('main loop returns false.')
        break
    self.log_d('AsyncHandler() ends')

  def __main_loop_iteration(self):
    self.log_d('__main_loop_iteration() starting')
    self._running_lock.acquire()
    running = self._running;
    self._running_lock.release()

    if not running:
      return False

    # get next message in queue
    self.log_d('__main_loop_iteration() waiting for message')
    data = self._queue.get(block = True, timeout = None)
    self.log_d('__main_loop_iteration() got message')

    if data == None:
      self.log_d('__main_loop_iteration() got terminate')
      self._queue.task_done()
      self._running_lock.acquire()
      self._running = False
      self._running_lock.release()
      return False
    else:
      self.log_d('__main_loop_iteration() got data')
      self._handler(data)
      self._queue.task_done()
    return True

  def stop(self):
    self._queue.put(None, block = False, timeout = None)
    self.join()
    assert not self.isAlive()

  def post(self, data):
    assert data != None, 'Data cannot be None'
    self.log_d('send(%s)' % (pprint.pformat(data)))
    self._queue.put(data, block = False, timeout = None)
