#!/usr/bin/env python
#-*- coding:utf-8 -*-

from thread_id_base import thread_id_base
import ctypes

class thread_id_linux(thread_id_base):

  _SYS_thread_id = 186
  _libc = ctypes.cdll.LoadLibrary('libc.so.6')

  @classmethod
  def thread_id(clazz):
    'Return the current thread id.'
    return clazz._libc.syscall(clazz._SYS_thread_id)
