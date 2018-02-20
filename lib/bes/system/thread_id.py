#!/usr/bin/env python
#-*- coding:utf-8 -*-

#from .impl_import import impl_import

#thread_id = impl_import.load(__name__, 'thread_id', globals())

from .thread_id_base import thread_id_base
import threading

class thread_id(thread_id_base):

  @classmethod
  def thread_id(clazz):
    'Return the current thread id.'
    return threading.current_thread().name
