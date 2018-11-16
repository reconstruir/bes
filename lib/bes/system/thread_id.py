#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .host import host
import threading

class thread_id(object):

  @classmethod
  def _thread_id_macos(clazz):
    return threading.current_thread().name

  @classmethod
  def _thread_id_linux_libc(clazz):
    if not hasattr(clazz, '_libc'):
      import ctypes
      setattr(clazz, '_libc', ctypes.cdll.LoadLibrary('libc.so.6'))
    return getattr(clazz, '_libc')
  
  @classmethod
  def _thread_id_linux(clazz):
    libc = clazz._thread_id_linux_libc()
    return libc.syscall(186)

  @classmethod
  def _thread_id_linux_arm(clazz):
    libc = clazz._thread_id_linux_libc()
    return libc.syscall(224)

  thread_id = None
  if host.SYSTEM == host.MACOS:
    thread_id = _thread_id_macos
  elif host.SYSTEM == host.LINUX:
    if host.ARCH.startswith('arm'):
      thread_id = _thread_id_linux_arm
    else:
      thread_id = _thread_id_linux
  assert thread_id
