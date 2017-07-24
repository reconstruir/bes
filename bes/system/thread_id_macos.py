#!/usr/bin/env python
#-*- coding:utf-8 -*-

from thread_id_base import thread_id_base
import threading

class thread_id_macos(thread_id_base):

  def __init__(self):
    super(thread_id_macos, self).__init__()
    
  def thread_id(self):
    'Return the current thread id.'
    return threading.current_thread().name
