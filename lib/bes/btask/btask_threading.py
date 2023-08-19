#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import multiprocessing
import threading

from bes.system.check import check

class btask_threading(object):

  @classmethod
  def is_main_process(clazz):
    return multiprocessing.parent_process() == None

  @classmethod
  def check_main_process(clazz, label = None):
    check.check_string(label, allow_none = True)

    label = f'{label}: ' if label else ''
    if not clazz.is_main_process():
      current = multiprocessing.current_process()
      raise btask_error(f'{label}Can only be called from the main process instead of "{current}"')

  @classmethod
  def is_main_thread(clazz):
    return threading.current_thread() == threading.main_thread()

  @classmethod
  def check_main_thread(clazz, label = None):
    check.check_string(label, allow_none = True)
    
    label = f'{label}: ' if label else ''
    if not clazz.is_main_thread():
      current = threading.current_thread()
      raise btask_error(f'{label}Can only be called from the main thread instead of "{current}"')

  @classmethod
  def current_process_pid(clazz):
    return multiprocessing.current_process().pid

  @classmethod
  def current_process_name(clazz):
    return multiprocessing.current_process().pid

  @classmethod
  def set_current_process_name(clazz, name):
    check.check_string(name, allow_none = True)

    multiprocessing.current_process().name = name
    assert multiprocessing.current_process().name == name
    #print(f'name={name} caca={multiprocessing.current_process().name}')
  
  @classmethod
  def current_thread_id(clazz):
    return threading.current_thread().ident

  @classmethod
  def current_thread_name(clazz):
    return threading.current_thread().name
  
