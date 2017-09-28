#!/usr/bin/env python
#-*- coding:utf-8 -*-

from bes.system import log
from .global_thread_pool import global_thread_pool
from functools import partial

class UiThreadCaller(object):
  def __init__(self):
    super(UiThreadCaller, self).__init__()

  def call_in_ui_thread(self, func):
    assert False, 'Not implemented'

class Scheduler(object):
  """Schedule code to be called at various times."""

  ui_thread_caller = None

  def __init__(self):
    super(Scheduler, self).__init__()
    log.add_logging(self, 'scheduler')

  @classmethod
  def set_ui_thread_caller(clazz, caller):
    'Set an implementation of UiThreadCaller.'
    assert caller, 'Caller cant be empty.'
    assert caller.call_in_ui_thread, 'Caller must have a call_in_ui_thread method.'
    clazz.ui_thread_caller = caller

  @classmethod
  def call_in_ui_thread(clazz, func, *args, **kargs):
    'Call the given function in the ui thread'
    assert clazz.ui_thread_caller, 'Ui Thread Caller not set.'
    callback = partial(func, *args, **kargs)
    clazz.ui_thread_caller.call_in_ui_thread(callback)

  @classmethod
  def call_in_global_thread_pool(clazz, func, *args, **kargs):
    'Call the given function in the global thread pool'
    global_thread_pool.add_task(func, *args, **kargs)
