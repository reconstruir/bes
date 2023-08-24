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
from .btask_task import btask_task

class btask_process(object):

  _log = logger('btask')
  
  def __init__(self, data):
    check.check_btask_process_data(data)

    self._data = data
    self._process = None

  @classmethod
  def _process_set_nice_level(clazz, name, nice_level):
    if nice_level == None:
      return
    old_nice_level = os.nice(0)
    new_nice_level = os.nice(nice_level)
    clazz._log.log_i(f'{name}: changed nice from {old_nice_level} to {new_nice_level}')

  @classmethod
  def _process_set_name(clazz, name):
    clazz._log.log_d(f'_process_set_name: name="{name}"')
    old_name = btask_threading.current_process_name()
    btask_threading.set_current_process_name(name)
    new_name = btask_threading.current_process_name()
    clazz._log.log_i(f'_process_set_name: changed process name from "{old_name}" to "{new_name}"')

  @classmethod
  def _process_run_initializer(clazz, name, initializer, initializer_args):
    if not initializer:
      return
    initializer_args = initializer_args or ()
    clazz._log.log_d(f'{name} calling initializer "{initializer}" with "{initializer_args}"')
    initializer(*initializer_args)

  @classmethod
  def _process_main_loop(clazz, name, input_queue, output_queue):
    while True:
      task = input_queue.get()
      if task == None:
        clazz._log.log_e(f'{name}: unexpected task type instead of btask_task: "{task}" - {type(task)}')
        break
      if not isinstance(task, btask_task):
        clazz._log.log_e(f'{name}: unexpected task type instead of btask_task: "{task}" - {type(task)}')
        continue
      clazz._task_handle(name, task, output_queue)
    return 0
    
  @classmethod
  def _process_main(clazz, encoded_task_data):
    check.check_bytes(encoded_task_data)

    task_data = pickle.loads(encoded_task_data)
    name = task_data.name
    clazz._log.log_d(f'{name}: task_data={task_data}')
    clazz._process_set_name(name)
    clazz._process_set_nice_level(name, task_data.nice_level)
    clazz._process_run_initializer(name, task_data.initializer, task_data.initializer_args)
    clazz._process_main_loop(name, task_data.input_queue, task_data.output_queue)
    return 0

  @classmethod
  def _task_handle(clazz, name, task, output_queue):
    clazz._log.log_d(f'{name}: _task_handle: task={task}')
    from datetime import datetime
    import time
    import os
#    time.sleep(.250)
    output_queue.put({ 'foo': datetime.now(), 'pid': os.getpid() })
    
  def start(self):
    if self._process:
      self._log.log_d(f'start: process already started')
      return

    encoded_task_data = pickle.dumps(self._data)
    self._process = multiprocessing.Process(target = self._process_main,
                                            args = ( encoded_task_data, ))
    self._process.start()

  def join(self):
    if not self._process:
      self._log.log_d(f'join: process not started')
      return
    self._process.join()
    
  def terminate(self):
    if not self._process:
      self._log.log_d(f'stop: process not started')
      return
    input_queue = task_data.input_queue

    
#  task_data = btask_data(_init, ( 'large', 10.2 ), input_queue, output_queue)
    

#self._data    
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
