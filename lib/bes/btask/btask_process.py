#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
from collections import namedtuple

import pickle
import multiprocessing
import os
import time

from bes.system.log import logger
from bes.system.check import check

from .btask_cancelled_error import btask_cancelled_error
from .btask_function_context import btask_function_context
from .btask_pool_item import btask_pool_item
from .btask_result import btask_result
from .btask_result_metadata import btask_result_metadata
from .btask_result_state import btask_result_state
from .btask_threading import btask_threading
from .btask_initializer import btask_initializer

class _process_data(namedtuple('_process_data', 'name, input_queue, result_queue, nice_level, initializer')):
  
  def __new__(clazz, name, input_queue, result_queue, nice_level = None,
              initializer = None):
    assert input_queue != None
    assert result_queue != None
    check.check_string(name)
    check.check_int(nice_level, allow_none = True)
    initializer = check.check_btask_initializer(initializer, allow_none = True)

    return clazz.__bases__[0].__new__(clazz, name, input_queue, result_queue,
                                      nice_level, initializer)

class btask_process(object):

  _log = logger('btask')
  
  def __init__(self, name, input_queue, result_queue, nice_level = None,
               initializer = None):
    assert input_queue != None
    assert result_queue != None
    check.check_string(name)
    check.check_int(nice_level, allow_none = True)
    initializer = check.check_btask_initializer(initializer, allow_none = True)

    self._data = _process_data(name,
                               input_queue,
                               result_queue,
                               nice_level = nice_level,
                               initializer = initializer)
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
  def _process_run_initializer(clazz, name, initializer):
    if not initializer:
      return
    clazz._log.log_d(f'{name} calling initializer "{initializer}"')
    initializer.call()

  @classmethod
  def _process_main_loop(clazz, name, input_queue, result_queue):
    while True:
      task = input_queue.get()
      if task == None:
        clazz._log.log_i(f'{name}: got termination sentinel.')
        break
      if not isinstance(task, btask_pool_item):
        clazz._log.log_e(f'{name}: unexpected task type instead of btask_pool_item: "{task}" - {type(task)}')
        continue
      clazz._task_handle(name, task, result_queue)
    return 0
    
  @classmethod
  def _process_main(clazz, encoded_task_data):
    check.check_bytes(encoded_task_data)

    task_data = pickle.loads(encoded_task_data)
    name = task_data.name
    clazz._log.log_d(f'{name}: task_data={task_data}')
    clazz._process_set_name(name)
    clazz._process_set_nice_level(name, task_data.nice_level)
    clazz._process_run_initializer(name, task_data.initializer)
    clazz._process_main_loop(name, task_data.input_queue, task_data.result_queue)
    return 0

  @classmethod
  def _task_handle(clazz, name, task, result_queue):
    clazz._log.log_d(f'{name}: _task_handle: task_id={task.task_id}')

#  def __new__(clazz, task_id, add_time, config, function, args, callback, progress_callback, cancelled):
#class btask_function_context(namedtuple('btask_function_context', 'task_id, progress_queue, cancelled_value')):
    start_time = datetime.now()
    add_time = start_time
    error = None
    result_data = None

    context = btask_function_context(task.task_id, result_queue, task.cancelled_value)
    debug = False
    try:
      result_data = task.function(context, task.args)
      #clazz._log.log_d(f'{name}: _task_handle:: task_id={task.task_id} data={result_data}')
      if not check.is_dict(result_data):
        raise btask_error(f'Function "{function}" should return a dict: "{result_data}" - {type(result_data)}')
      state = btask_result_state.SUCCESS
    except Exception as ex:
      if debug:
        clazz._log.log_exception(ex)
      if isinstance(ex, btask_cancelled_error):
        state = btask_result_state.CANCELLED
        error = None
      else:
        state = btask_result_state.FAILED
        error = ex

    end_time = datetime.now()
    clazz._log.log_d(f'{name}: _task_handle:: task_id={task.task_id} state={state}')
    metadata = btask_result_metadata(btask_threading.current_process_pid(),
                                     add_time,
                                     start_time,
                                     end_time)
    result = btask_result(task.task_id, state, result_data, metadata, error, task.args)
        
    result_queue.put(result)
    
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
    # drain the queue first ?
    
#  task_data = btask_data(_init, ( 'large', 10.2 ), input_queue, result_queue)
    

#self._data    
    '''
  manager = multiprocessing.Manager()
  input_queue = manager.Queue()
  result_queue = manager.Queue()
  task_data = btask_data(_init, ( 'large', 10.2 ), input_queue, result_queue)
  data = {
    'color': 'green',
    'flavor': 'tart',
    'price': 6.66,
    'init': _init,
    'init_args': ( 'large', 10.2 ),
    'input_queue': input_queue,
    'result_queue': result_queue,
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
