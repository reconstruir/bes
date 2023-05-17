#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import queue as py_queue

from .btask_main_thread_runner_i import btask_main_thread_runner_i

class btask_main_thread_runner_py(btask_main_thread_runner_i):

  def __init__(self):
    self._queue = py_queue.Queue()
  
  #@abstractmethod
  def call_in_main_thread(self, function, *args, **kwargs):
    self._queue.put(( function, args, kwargs) )

  def main_loop_stop(self):
    self._queue.put(( None, None, None ) )
    
  def main_loop_start(self):
    while True:
#      try:
      function, args, kwargs = self._queue.get(True)
      if function == None:
        return
      function(*args, **kwargs)
#      except py_queue.Empty: #raised when queue is empty
#        break
