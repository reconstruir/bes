#!/usr/bin/env python
#-*- coding:utf-8 -*-

from .thread_id_base import thread_id_base
import threading

class thread_id_macos(thread_id_base):

  @classmethod
  def thread_id(clazz):
    'Return the current thread id.'
    return threading.current_thread().name
