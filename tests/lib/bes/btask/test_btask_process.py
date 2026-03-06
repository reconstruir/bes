#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import time
import os
import queue
from datetime import timedelta
from datetime import datetime
import threading
import multiprocessing

from bes.system.check import check
from bes.system.execute_result import execute_result
from bes.system.log import logger
from bes.testing.unit_test import unit_test

from bes.btask.btask_process import btask_process
from bes.btask.btask_process_task import btask_process_task
from bes.btask.btask_result import btask_result
from bes.btask._btask_status_queue_item import _btask_status_queue_item
from bes.btask.btask_status_step_progress import btask_status_step_progress

class test_btask_process(unit_test):

  _log = logger('test')

  @classmethod
  def _function(clazz, context, args):
    clazz._log.log_d(f'_function: task_id={context.task_id} args={args}')
    result_error = args.get('__f_result_error', None)
    sleep_time_ms = args.get('__f_sleep_time_ms', None)
    if sleep_time_ms != None:
      sleep_time = (float(sleep_time_ms) / 1000.0) * 1.1
      time.sleep(sleep_time)
    if result_error:
      raise result_error
    result_data = args.get('__f_result_data', None) or {}
    result_data['pid'] = os.getpid()
    return result_data

  @classmethod
  def _fix_args(clazz, args):
    result = {}
    for key, value in args.items():
      if not key.startswith('__f_'):
        result[key] = value
    return result

  @classmethod
  def _run_task_and_collect(clazz, manager, function, args, timeout = 5.0):
    '''Run a single task and collect all status items and the final result.
    Returns (status_items, btask_result).'''
    input_queue = manager.Queue()
    result_queue = manager.Queue()
    process = btask_process('test_worker', input_queue, result_queue)
    process.start()
    cancelled_value = manager.Value(bool, False)
    task = btask_process_task(1,
                              datetime.now(),
                              ( 'test', 'low', 2, False ),
                              function,
                              args,
                              cancelled_value)
    input_queue.put(task)

    status_items = []
    final_result = None
    deadline = time.monotonic() + timeout
    while final_result is None:
      remaining = deadline - time.monotonic()
      if remaining <= 0:
        raise TimeoutError('timed out waiting for task result')
      try:
        item = result_queue.get(timeout = remaining)
      except Exception:
        raise TimeoutError('timed out waiting for task result')
      if isinstance(item, btask_result):
        final_result = item
      elif isinstance(item, _btask_status_queue_item):
        status_items.append(item)

    input_queue.put(None)
    process.join()
    return status_items, final_result

  @classmethod
  def _step_status_items(clazz, status_items):
    return [ i for i in status_items if isinstance(i.status, btask_status_step_progress) ]

  # --- original tests ---

  def test_process_one_process(self):
    self._log.log_d(f'test_process_one_process:')

    manager = multiprocessing.Manager()
    input_queue = manager.Queue()
    result_queue = manager.Queue()

    process = btask_process('kiwi1', input_queue, result_queue)
    process.start()

    cancelled_value = manager.Value(bool, False)
    task = btask_process_task(42,
                              datetime.now(),
                              ( 'kiwi', 'low', 2, self.DEBUG ),
                              self._function,
                              {
                                'number': 42,
                                'flavor': 'sweet',
                                '__f_result_data': { 'fruit': 'kiwi', 'color': 'green' },
                              },
                              cancelled_value)
    input_queue.put(task)

    result = result_queue.get()
    input_queue.put(None)
    process.join()

  def test_process_many_processes(self):
    manager = multiprocessing.Manager()
    input_queue = manager.Queue()
    result_queue = manager.Queue()

    num_processes = 10
    num_tasks = 100

    processes = []
    for i in range(1, num_processes + 1):
      name = f'kiwi{i}'
      process = btask_process(name, input_queue, result_queue)
      processes.append(process)
      process.start()

    for i in range(1, num_tasks + 1):
      cancelled_value = manager.Value(bool, False)
      task = btask_process_task(42 + i,
                                datetime.now(),
                                ( 'kiwi', 'low', 2, self.DEBUG ),
                                self._function,
                                {
                                  'number': i,
                                  'flavor': 'sweet',
                                  '__f_result_data': { 'fruit': 'kiwi', 'color': 'green' },
                                },
                                cancelled_value)
      input_queue.put(task)

    results = []
    for i in range(1, num_tasks + 1):
      result = result_queue.get()
      results.append(result)

    for i in range(1, num_processes + 1):
      input_queue.put(None)

    for process in processes:
      process.join()

    for result in results:
      print(result.to_json())

  # --- step progress tests ---

  @classmethod
  def _fn_step_basic(clazz, context, args):
    context.report_step_progress(step = 1, total_steps = 3,
                                 step_title = 'file.mp4', step_percent = 50)
    return {}

  def test_report_step_progress_basic(self):
    manager = multiprocessing.Manager()
    status_items, result = self._run_task_and_collect(manager, self._fn_step_basic, {})
    step_items = self._step_status_items(status_items)
    self.assertEqual(1, len(step_items))
    sp = step_items[0].status.step_progress
    self.assertEqual(1, sp.step)
    self.assertEqual(3, sp.total_steps)
    self.assertEqual('file.mp4', sp.step_title)
    self.assertEqual(50, sp.step_percent)

  @classmethod
  def _fn_step_indeterminate(clazz, context, args):
    context.report_step_progress(step = 1, total_steps = 1,
                                 step_title = 'working', step_percent = None)
    return {}

  def test_report_step_progress_indeterminate(self):
    manager = multiprocessing.Manager()
    status_items, result = self._run_task_and_collect(manager, self._fn_step_indeterminate, {})
    step_items = self._step_status_items(status_items)
    self.assertEqual(1, len(step_items))
    sp = step_items[0].status.step_progress
    self.assertIsNone(sp.step_percent)

  @classmethod
  def _fn_step_preparation_sentinel(clazz, context, args):
    context.report_step_progress(step = 0, total_steps = None,
                                 step_title = 'Scanning...', step_percent = None)
    return {}

  def test_report_step_progress_preparation_sentinel(self):
    manager = multiprocessing.Manager()
    status_items, result = self._run_task_and_collect(manager, self._fn_step_preparation_sentinel, {})
    step_items = self._step_status_items(status_items)
    self.assertEqual(1, len(step_items))
    sp = step_items[0].status.step_progress
    self.assertEqual(0, sp.step)
    self.assertIsNone(sp.total_steps)

  @classmethod
  def _fn_step_throttle_drops_duplicates(clazz, context, args):
    for _ in range(50):
      context.report_step_progress(step = 1, total_steps = 1,
                                   step_title = 'processing', step_percent = 42)
    return {}

  def test_report_step_progress_throttle_drops_duplicates(self):
    manager = multiprocessing.Manager()
    status_items, result = self._run_task_and_collect(manager,
                                                      self._fn_step_throttle_drops_duplicates, {})
    step_items = self._step_status_items(status_items)
    self.assertEqual(1, len(step_items))

  @classmethod
  def _fn_step_throttle_passes_distinct(clazz, context, args):
    for pct in range(11):
      context.report_step_progress(step = 1, total_steps = 1,
                                   step_title = 'processing', step_percent = pct)
    return {}

  def test_report_step_progress_throttle_passes_distinct(self):
    manager = multiprocessing.Manager()
    status_items, result = self._run_task_and_collect(manager,
                                                      self._fn_step_throttle_passes_distinct, {})
    step_items = self._step_status_items(status_items)
    self.assertEqual(11, len(step_items))
    percents = [ i.status.step_progress.step_percent for i in step_items ]
    self.assertEqual(list(range(11)), percents)

  @classmethod
  def _fn_step_warn_threshold(clazz, context, args):
    # 101 identical calls: first passes, next 99 are dropped silently,
    # the 100th duplicate triggers the warning log and returns
    for _ in range(101):
      context.report_step_progress(step = 1, total_steps = 1,
                                   step_title = 'processing', step_percent = 5)
    return {}

  def test_report_step_progress_throttle_warn_threshold(self):
    manager = multiprocessing.Manager()
    status_items, result = self._run_task_and_collect(manager,
                                                      self._fn_step_warn_threshold, {})
    step_items = self._step_status_items(status_items)
    # Only the very first call passes; all 100 duplicates are dropped
    self.assertEqual(1, len(step_items))

  @classmethod
  def _fn_step_indeterminate_to_determinate(clazz, context, args):
    context.report_step_progress(step = 0, total_steps = None,
                                 step_title = 'Scanning...', step_percent = None)
    context.report_step_progress(step = 1, total_steps = 5,
                                 step_title = 'file1.mp4', step_percent = 0)
    return {}

  def test_report_step_progress_indeterminate_to_determinate_transition(self):
    manager = multiprocessing.Manager()
    status_items, result = self._run_task_and_collect(
      manager, self._fn_step_indeterminate_to_determinate, {})
    step_items = self._step_status_items(status_items)
    self.assertEqual(2, len(step_items))
    sp0 = step_items[0].status.step_progress
    self.assertEqual(0, sp0.step)
    self.assertIsNone(sp0.total_steps)
    sp1 = step_items[1].status.step_progress
    self.assertEqual(1, sp1.step)
    self.assertEqual(5, sp1.total_steps)
    self.assertEqual(0, sp1.step_percent)

if __name__ == '__main__':
  unit_test.main()
