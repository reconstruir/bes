#!/usr/bin/env python
#-*- coding:utf-8 -*-

from thread_id_base import thread_id_base
from impl_loader import impl_loader

class thread_id(thread_id_base):
  'Top level class for dealing with system thread_ids.'

  __impl = impl_loader.load(__file__, 'thread_id')

  @classmethod
  def thread_id(clazz):
    'Return the current thread id.'
    return clazz.__impl.thread_id()
