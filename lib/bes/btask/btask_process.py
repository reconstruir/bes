#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime

import pickle
import multiprocessing
import os
import time

from bes.system.log import logger
from bes.system.check import check

from .btask_process_data import btask_process_data
from .btask_threading import btask_threading

class btask_process(object):

  _log = logger('btask')
  
  def __init__(self, data):
    check.check_btask_process_data(data)

    self._data = data
    self._process = None

  @classmethod
  def _process_main(clazz, encoded_task_data):
    check.check_bytes(encoded_task_data)

    decoded_task_data = pickle.loads(encoded_task_data)
    name = decoded_task_data.name
    clazz._log.log_d(f'{name}: decoded_task_data={decoded_task_data}')
    clazz._process_set_name(name)
    clazz._process_set_nice_level(name, nice_level)
    clazz._process_run_initializer(name, initializer, initializer_args):    
      
    input_queue = decoded_task_data.input_queue
    output_queue = decoded_task_data.output_queue
    while True:
      task = input_queue.get()
      if task == None:
        break
  return 0

  @classmethod
  def _process_set_nice_level(clazz, name, nice_level):
    if nice_level == None:
      return
    old_nice_level = os.nice(0)
    new_nice_level = os.nice(nice_level)
    clazz._log.log_i(f'{name}: changed nice from {old_nice_level} to {new_nice_level}')

  @classmethod
  def _process_set_name(clazz, name):
    old_name = btask_threading.current_process_name()
    btask_threading.set_current_process_name(name)
    new_name = btask_threading.current_process_name()
    clazz._log.log_i(f'changed process name from "{old_name}" to "{new_name}"')

  @classmethod
  def _process_run_initializer(clazz, name, initializer, initializer_args):
    if not initializer:
      return
    initializer_args = initializer_args or ()
    clazz._log.log_d(f'{name} calling initializer "{initializer}" with "{initializer_args}"')
    initializer(*initializer_args)
    
  def start(self):
    if self._process:
      self._log.log_d(f'start: process already started')
      return
    '''
  manager = multiprocessing.Manager()
  input_queue = manager.Queue()
  output_queue = manager.Queue()
  task_data = btask_data(_init, ( 'large', 10.2 ), input_queue, output_queue)
  data = {
    'color': 'green',
    'flavor': 'tart',
    'price': 6.66,
    'init': _init,
    'init_args': ( 'large', 10.2 ),
    'input_queue': input_queue,
    'output_queue': output_queue,
  }

  item = bprocess_pool_item(1, datetime.now(), None, function, args, callback, progress_callback, cancelled)
  
  encoded_task_data = pickle.dumps(task_data)
  p = multiprocessing.Process (name = 'ppp',
                              target = _process,
                              args = ( encoded_task_data, ))
  p.start()
  p.join()
  exit_code = p.exitcode
  _log.log_d(f'exit_code={exit_code}')
  return 0
'''  
  def stop(self):
    pass
  
check.register_class(btask_process, include_seq = False)
