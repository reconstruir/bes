#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import signal
import time

from collections import namedtuple
from datetime import datetime
import multiprocessing
import threading

from bes.system.log import logger
from bes.system.check import check

from .btask_error import btask_error
from .btask_task import btask_task
from .btask_process_task import btask_process_task
from .btask_result import btask_result
from .btask_result_metadata import btask_result_metadata
from .btask_result_state import btask_result_state
from .btask_status import btask_status
from ._btask_status_queue_item import _btask_status_queue_item
from ._btask_task_started_item import _btask_task_started_item
from .btask_threading import btask_threading
from .btask_process import btask_process
from .btask_initializer import btask_initializer

class btask_process_pool(object):

  _log = logger('btask')

  def __init__(self, name, num_processes, manager, initializer = None):
    check.check_string(name)
    check.check_int(num_processes)
    initializer = check.check_btask_initializer(initializer, allow_none = True)
    self._log.log_method_d()
    self._name = name
    self._num_processes = num_processes
    self._initializer = initializer
    self._manager = manager
    self._input_queue = self._manager.Queue()
    self._process_result_queue = self._manager.Queue()
    self._worker_number_lock = self._manager.Lock()
    self._worker_number_value = self._manager.Value(int, 1)
    self._processes = None
    self._result_thread = None
    self._task_callbacks = {}
    self._task_callbacks_lock = threading.Lock()

    # timeout support
    self._task_pid_map = {}           # task_id → worker pid
    self._task_start_time_map = {}    # task_id → datetime when worker started
    self._task_add_time_map = {}      # task_id → add_time from the submitted task
    self._grace_timers = {}           # task_id → threading.Timer
    self._task_pid_map_lock = threading.Lock()

  def _run_result_thread(self):
    btask_threading.set_current_thread_name(f'{self._name}_result_thread')
    self._log.log_d(f'_run_result_thread: starting')
    while True:
      next_result = self._process_result_queue.get()
      if next_result is None:
        self._log.log_d(f'_run_result_thread: got termination sentinel')
        break
      task_id = next_result.task_id
      is_result = isinstance(next_result, btask_result)
      is_progress = isinstance(next_result, _btask_status_queue_item)
      is_started = isinstance(next_result, _btask_task_started_item)
      type_name = type(next_result).__name__
      self._log.log_d(f'_run_result_thread: got item task_id={task_id} type={type_name}')

      if not (is_result or is_progress or is_started):
        self._log.log_e(f'_run_result_thread: unexpected type "{type_name}" task_id={task_id}')
        continue

      if is_started:
        with self._task_pid_map_lock:
          self._task_pid_map[task_id] = next_result.pid
          self._task_start_time_map[task_id] = datetime.now()
        # started item is handled internally; do not forward to callback
        continue
      elif is_result:
        with self._task_pid_map_lock:
          self._task_pid_map.pop(task_id, None)
          self._task_start_time_map.pop(task_id, None)
          self._task_add_time_map.pop(task_id, None)
          timer = self._grace_timers.pop(task_id, None)
        if timer:
          timer.cancel()

      callback = None
      with self._task_callbacks_lock as lock:
        if task_id not in self._task_callbacks:
          if is_result and next_result.state == btask_result_state.TIMED_OUT:
            # synthesized duplicate from _hard_kill after soft cancel already delivered result
            self._log.log_d(f'_run_result_thread: dropping duplicate TIMED_OUT for task_id={task_id}')
          else:
            self._log.log_e(f'_run_result_thread: task {task_id} not found in callbacks')
          continue
        callback = self._task_callbacks[task_id]
        if is_result:
          del self._task_callbacks[task_id]
      assert callback is not None
      callback(next_result)

  def _processes_start(self):
    processes = []
    for i in range(1, self._num_processes + 1):
      process_name = f'{self._name}_worker_{i}'
      process = btask_process(process_name,
                              self._input_queue,
                              self._process_result_queue,
                              nice_level = None,
                              initializer = self._initializer)
      processes.append(process)
    for process in processes:
      process.start()
    return processes

  @classmethod
  def _processes_stop(self, processes, input_queue):
    for _ in processes:
      input_queue.put(None)
    for process in processes:
      self._log.log_i(f'_processes_stop: joining process {process.name}')
      process.join()

  def start(self):
    if self._processes:
      self._log.log_d(f'start: pool already started')
      return
    self._processes = self._processes_start()
    self._result_thread = threading.Thread(target = self._run_result_thread,
                                           name = f'{self._name}_result_thread',
                                           daemon = True)
    self._result_thread.start()

  def stop(self):
    if not self._processes:
      self._log.log_d(f'stop: pool not started')
      return
    self._process_result_queue.put(None)
    self._result_thread.join()
    self._result_thread = None
    self._processes_stop(self._processes, self._input_queue)
    self._processes = None

  @property
  def num_processes(self):
    return self._num_processes

  def add_task(self, task, callback):
    check.check_btask_task(task)
    check.check_callable(callback)

    task_id = task.task_id
    with self._task_callbacks_lock as lock:
      if task_id in self._task_callbacks:
        raise btask_error(f'Task {task_id} is already in process.')
      self._task_callbacks[task_id] = callback
    with self._task_pid_map_lock:
      self._task_add_time_map[task_id] = task.add_time
    process_task = btask_process_task(task.task_id,
                                      task.add_time,
                                      task.config,
                                      task.function,
                                      task.args,
                                      task.cancelled_value)
    self._input_queue.put(process_task)

  def start_grace_timer(self, task_id, grace_seconds):
    check.check_int(task_id)
    check.check_int(grace_seconds)

    with self._task_pid_map_lock:
      pid = self._task_pid_map.get(task_id)
    if pid is None:
      # worker hasn't sent started item yet or task already completed;
      # soft cancel is sufficient — no hard kill needed
      return
    timer = threading.Timer(float(grace_seconds), self._hard_kill, args = (task_id, pid))
    timer.daemon = True
    with self._task_pid_map_lock:
      self._grace_timers[task_id] = timer
    timer.start()

  def _hard_kill(self, task_id, pid):
    self._log.log_d(f'_hard_kill: task_id={task_id} pid={pid}')
    try:
      os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
      return  # already exited — soft cancel worked; result already in flight
    time.sleep(0.5)
    try:
      os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
      pass  # died from SIGTERM during the sleep
    self._emit_timed_out_result(task_id)
    self._respawn_worker()

  def _emit_timed_out_result(self, task_id):
    with self._task_pid_map_lock:
      if task_id not in self._task_pid_map:
        # soft cancel already delivered a result and the result thread cleaned up maps
        return
      pid = self._task_pid_map.pop(task_id, 0)
      start_time = self._task_start_time_map.pop(task_id, None)
      add_time = self._task_add_time_map.pop(task_id, datetime.now())
      self._grace_timers.pop(task_id, None)
    end_time = datetime.now()
    actual_start = start_time or add_time
    metadata = btask_result_metadata(pid, add_time, actual_start, end_time)
    result = btask_result(task_id, btask_result_state.TIMED_OUT, None, metadata, None, {})
    self._process_result_queue.put(result)

  def _respawn_worker(self):
    self._log.log_d(f'_respawn_worker: spawning replacement worker for {self._name}')
    process_name = f'{self._name}_respawn_{datetime.now().strftime("%H%M%S%f")}'
    process = btask_process(process_name,
                            self._input_queue,
                            self._process_result_queue,
                            nice_level = None,
                            initializer = self._initializer)
    process.start()
    if self._processes is not None:
      self._processes.append(process)

check.register_class(btask_process_pool, include_seq = False)
