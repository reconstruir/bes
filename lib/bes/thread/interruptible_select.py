#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, select
import threading
from decorators import synchronized_method

class InterruptibleSelect(object):
  'An interruptible version of select'

  DATA_AVAILABLE = 1 << 0
  INTERRUPTED = 1 << 1

  def __init__(self, fd):
    super(InterruptibleSelect, self).__init__()
    self._fd = fd
    self._lock = threading.Lock()
    self._select_thread = None
    self._pipe = os.pipe()

  def select(self, timeout):
    self.__set_select_thread(threading.currentThread())
    read_fds = [ self._fd, self._pipe[0] ]
    write_fds = []
    except_fds = []
    inputready, outputready, exceptready = select.select(read_fds, write_fds, except_fds, timeout) 
    result = 0
    if self._fd in inputready:
      result |= self.__class__.DATA_AVAILABLE
    if self._pipe[0] in inputready:
      os.read(self._pipe[0], 1)
      result |= self.__class__.INTERRUPTED
    self.__set_select_thread(None)
    return result

  @synchronized_method('_lock')
  def __set_select_thread(self, t):
    self._select_thread = t

  @synchronized_method('_lock')
  def interrupt(self):
    if self._select_thread == threading.currentThread():
      raise RuntimeError('Cannot interrupt the from the same thread as select.')
    os.write(self._pipe[1], 'x')

  @staticmethod
  def data_available(result):
    return (result & InterruptibleSelect.DATA_AVAILABLE) != 0

  @staticmethod
  def interrupted(result):
    return (result & InterruptibleSelect.INTERRUPTED) != 0

