#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import time
from datetime import timedelta

from bes.testing.unit_test import unit_test

from bes.btask.btask_config import btask_config
from bes.btask.btask_processor_tester_py import btask_processor_tester_py
from bes.btask.btask_result_state import btask_result_state

class test_btask_timeout(unit_test):

  @classmethod
  def _fn_sleep_forever(clazz, context, args):
    'Simulates a stuck task — ignores cancellation, sleeps effectively forever.'
    time.sleep(3600)
    return {}

  @classmethod
  def _fn_sleep_with_cancel_check(clazz, context, args):
    'Simulates a well-behaved long task — checks cancellation every 50 ms.'
    for _ in range(200):
      time.sleep(0.050)
      context.raise_cancelled_if_needed('cancelled')
    return {}

  @classmethod
  def _fn_fast(clazz, context, args):
    'Completes immediately.'
    return {'done': True}

  @classmethod
  def _fn_sleep_short(clazz, context, args):
    time.sleep(0.1)
    return {}

  def _config(self, timeout_seconds = None, kill_grace_seconds = 5, limit = 3):
    return btask_config('rip',
                        limit = limit,
                        timeout_seconds = timeout_seconds,
                        kill_grace_seconds = kill_grace_seconds)

  def test_timeout_result_state(self):
    'A stuck task with a timeout should produce a timed_out result.'
    tester = btask_processor_tester_py('test', 2)
    task_id = tester.add_task(self._fn_sleep_forever,
                              callback = lambda r: tester.on_callback(r),
                              config = self._config(timeout_seconds = 2, kill_grace_seconds = 1))
    tester.start()
    results = tester.results()
    tester.stop()

    r = results[task_id]
    self.assertEqual('timed_out', r.state)

  def test_timeout_completes_before_deadline(self):
    'A task that finishes before the deadline should succeed normally.'
    tester = btask_processor_tester_py('test', 2)
    task_id = tester.add_task(self._fn_sleep_short,
                              callback = lambda r: tester.on_callback(r),
                              config = self._config(timeout_seconds = 5))
    tester.start()
    results = tester.results()
    tester.stop()

    r = results[task_id]
    self.assertEqual('success', r.state)

  def test_timeout_callback_called(self):
    'The task callback should be called exactly once with a timed_out result.'
    tester = btask_processor_tester_py('test', 2)
    call_count = [0]
    def _cb(r):
      call_count[0] += 1
      tester.on_callback(r)

    task_id = tester.add_task(self._fn_sleep_forever,
                              callback = _cb,
                              config = self._config(timeout_seconds = 2, kill_grace_seconds = 1))
    tester.start()
    results = tester.results()
    tester.stop()

    self.assertEqual(1, call_count[0])
    self.assertEqual('timed_out', results[task_id].state)

  def test_timeout_soft_cancel_respected(self):
    'A task that checks cancellation should get timed_out (not cancelled) after timeout fires.'
    tester = btask_processor_tester_py('test', 2)
    task_id = tester.add_task(self._fn_sleep_with_cancel_check,
                              callback = lambda r: tester.on_callback(r),
                              config = self._config(timeout_seconds = 2, kill_grace_seconds = 5))
    tester.start()
    results = tester.results()
    tester.stop()

    r = results[task_id]
    # must be timed_out, not cancelled — the soft cancel is converted
    self.assertEqual('timed_out', r.state)

  def test_timeout_hard_kill(self):
    'A stuck task should be hard-killed and produce timed_out within a bounded time.'
    tester = btask_processor_tester_py('test', 2)
    start = time.time()
    task_id = tester.add_task(self._fn_sleep_forever,
                              callback = lambda r: tester.on_callback(r),
                              config = self._config(timeout_seconds = 2, kill_grace_seconds = 1))
    tester.start()
    results = tester.results()
    tester.stop()
    elapsed = time.time() - start

    r = results[task_id]
    self.assertEqual('timed_out', r.state)
    # timeout (2-3s watchdog window) + grace (1s) + 0.5s sigterm→sigkill + margin
    self.assertLess(elapsed, 8.0)

  def test_pool_self_heals_after_timeout(self):
    'After a hard-killed timeout the pool should respawn a worker and complete further tasks.'
    tester = btask_processor_tester_py('test', 1)
    stuck_config = self._config(timeout_seconds = 2, kill_grace_seconds = 1, limit = 1)
    fast_config = self._config(timeout_seconds = None, limit = 1)

    stuck_id = tester.add_task(self._fn_sleep_forever,
                               callback = lambda r: tester.on_callback(r),
                               config = stuck_config)
    fast_id = tester.add_task(self._fn_fast,
                              callback = lambda r: tester.on_callback(r),
                              config = fast_config)
    tester.start()
    results = tester.results()
    tester.stop()

    self.assertEqual('timed_out', results[stuck_id].state)
    self.assertEqual('success', results[fast_id].state)
    self.assertEqual(True, results[fast_id].data.get('done'))

  def test_multiple_tasks_one_times_out(self):
    'Timeout of one task should not affect other tasks running in parallel.'
    tester = btask_processor_tester_py('test', 3)
    fast_config = self._config(limit = 3)
    timeout_config = self._config(timeout_seconds = 2, kill_grace_seconds = 1, limit = 3)

    fast_id1 = tester.add_task(self._fn_fast,
                               callback = lambda r: tester.on_callback(r),
                               config = fast_config)
    fast_id2 = tester.add_task(self._fn_fast,
                               callback = lambda r: tester.on_callback(r),
                               config = fast_config)
    stuck_id = tester.add_task(self._fn_sleep_forever,
                               callback = lambda r: tester.on_callback(r),
                               config = timeout_config)
    tester.start()
    results = tester.results()
    tester.stop()

    self.assertEqual('success', results[fast_id1].state)
    self.assertEqual('success', results[fast_id2].state)
    self.assertEqual('timed_out', results[stuck_id].state)

  def test_multiple_tasks_all_time_out(self):
    'Multiple stuck tasks all time out; pool self-heals and subsequent tasks succeed.'
    tester = btask_processor_tester_py('test', 3)
    timeout_config = self._config(timeout_seconds = 2, kill_grace_seconds = 1, limit = 3)
    fast_config = self._config(limit = 3)

    stuck_id1 = tester.add_task(self._fn_sleep_forever,
                                callback = lambda r: tester.on_callback(r),
                                config = timeout_config)
    stuck_id2 = tester.add_task(self._fn_sleep_forever,
                                callback = lambda r: tester.on_callback(r),
                                config = timeout_config)
    stuck_id3 = tester.add_task(self._fn_sleep_forever,
                                callback = lambda r: tester.on_callback(r),
                                config = timeout_config)
    fast_id = tester.add_task(self._fn_fast,
                              callback = lambda r: tester.on_callback(r),
                              config = fast_config)
    tester.start()
    results = tester.results()
    tester.stop()

    self.assertEqual('timed_out', results[stuck_id1].state)
    self.assertEqual('timed_out', results[stuck_id2].state)
    self.assertEqual('timed_out', results[stuck_id3].state)
    self.assertEqual('success', results[fast_id].state)

  def test_timeout_metadata(self):
    'A timed-out task result should have a duration >= timeout_seconds.'
    tester = btask_processor_tester_py('test', 2)
    task_id = tester.add_task(self._fn_sleep_forever,
                              callback = lambda r: tester.on_callback(r),
                              config = self._config(timeout_seconds = 2, kill_grace_seconds = 1))
    tester.start()
    results = tester.results()
    tester.stop()

    r = results[task_id]
    self.assertEqual('timed_out', r.state)
    self.assertGreaterEqual(r.metadata.duration, timedelta(seconds = 2))

  def test_no_timeout_set(self):
    'A task with no timeout_seconds should complete normally even if it runs a while.'
    tester = btask_processor_tester_py('test', 2)
    task_id = tester.add_task(self._fn_sleep_short,
                              callback = lambda r: tester.on_callback(r),
                              config = self._config(timeout_seconds = None))
    tester.start()
    results = tester.results()
    tester.stop()

    r = results[task_id]
    self.assertEqual('success', r.state)

  def test_timeout_waiting_task(self):
    'A task in the waiting queue should time out and get timed_out state.'
    tester = btask_processor_tester_py('test', 1)
    # limit=1 so only one task can be in-progress at a time
    stuck_config = self._config(timeout_seconds = 4, kill_grace_seconds = 1, limit = 1)
    waiting_config = self._config(timeout_seconds = 2, kill_grace_seconds = 1, limit = 1)

    stuck_id = tester.add_task(self._fn_sleep_forever,
                               callback = lambda r: tester.on_callback(r),
                               config = stuck_config)
    waiting_id = tester.add_task(self._fn_sleep_forever,
                                 callback = lambda r: tester.on_callback(r),
                                 config = waiting_config)
    tester.start()
    results = tester.results()
    tester.stop()

    # waiting task timed out without ever starting — start_time should be None
    r = results[waiting_id]
    self.assertEqual('timed_out', r.state)
    self.assertIsNone(r.metadata.start_time)

    # stuck task also timed out
    self.assertEqual('timed_out', results[stuck_id].state)

  def test_timeout_in_progress_multiple_pools(self):
    'Two stuck tasks in separate categories both time out independently.'
    tester = btask_processor_tester_py('test', 4)
    config_a = btask_config('rip_a', limit = 1,
                            timeout_seconds = 2, kill_grace_seconds = 1)
    config_b = btask_config('rip_b', limit = 1,
                            timeout_seconds = 2, kill_grace_seconds = 1)
    fast_config_a = btask_config('rip_a', limit = 1)
    fast_config_b = btask_config('rip_b', limit = 1)

    stuck_id_a = tester.add_task(self._fn_sleep_forever,
                                 callback = lambda r: tester.on_callback(r),
                                 config = config_a)
    stuck_id_b = tester.add_task(self._fn_sleep_forever,
                                 callback = lambda r: tester.on_callback(r),
                                 config = config_b)
    fast_id_a = tester.add_task(self._fn_fast,
                                callback = lambda r: tester.on_callback(r),
                                config = fast_config_a)
    fast_id_b = tester.add_task(self._fn_fast,
                                callback = lambda r: tester.on_callback(r),
                                config = fast_config_b)
    tester.start()
    results = tester.results()
    tester.stop()

    self.assertEqual('timed_out', results[stuck_id_a].state)
    self.assertEqual('timed_out', results[stuck_id_b].state)
    self.assertEqual('success', results[fast_id_a].state)
    self.assertEqual('success', results[fast_id_b].state)

if __name__ == '__main__':
  unit_test.main()
