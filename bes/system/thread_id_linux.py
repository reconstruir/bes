#!/usr/bin/env python
#-*- coding:utf-8 -*-

from thread_id_base import thread_id_base
import ctypes

class thread_id_linux(thread_id_base):

  def __init__(self):
    super(thread_id_linux, self).__init__()
    #224 on arm
    self._SYS_thread_id = 186
    self._libc = ctypes.cdll.LoadLibrary('libc.so.6')
    
  def thread_id(self):
    'Return the current thread id.'
    return self._libc.syscall(self._SYS_thread_id)
