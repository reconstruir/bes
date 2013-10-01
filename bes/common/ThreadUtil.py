#!/usr/bin/env python
#-*- coding:utf-8 -*-

import threading

from System import System

class ThreadUtil(object):
  'Thread stuff'

  if System.is_linux():
    try:
      import ctypes
      _SYS_gettid = 186
      _libc = ctypes.cdll.LoadLibrary('libc.so.6')
    except:
      _libc = None

  @classmethod
  def gettid(clazz):
    if System.is_linux():
      if clazz._libc:
        return clazz._libc.syscall(clazz._SYS_gettid)
      else:
        return threading.current_thread().name
    elif System.is_mac():
      return threading.current_thread().name
    else:
      raise RuntimeError('System not supported')
