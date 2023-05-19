#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import threading

from bes.system.log import logger
from bes.system.check import check
from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

class btask_result_collector_i(with_metaclass(ABCMeta, object)):

  _log = logger('btask')

  def __init__(self, queue):
    self._queue = queue
    self._thread = None

  @abstractmethod
  def handle_result(self, result):
    raise NotImplemented('handle_result')
    
  def _thread_main(self):
    while True:
      result = self._queue.get()
      if result == None:
        break
      self.handle_result(result)
    return 0
  
  def start(self):
    if self._thread:
      return
    self._thread = threading.Thread(target = self._thread_main, args = ())
    self._thread.start()

  def stop(self):
    if not self._thread:
      return
    self._queue.put(None)
    self._thread.join()
    self._thread = None
    
check.register_class(btask_result_collector_i, name = 'btask_result_collector', include_seq = False)
