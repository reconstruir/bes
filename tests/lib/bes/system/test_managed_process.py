#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest.mock as mock

from bes.system.managed_process_generic import managed_process_generic
from bes.system.system_command_generic import system_command_generic
from bes.system.system_error import system_error
from bes.testing.unit_test import unit_test

class test_managed_process(unit_test):

  def test_happy_path(self):
    'launch succeeds, poll_ready is truthy immediately -- start() returns it, stop() tears down.'
    launch = mock.MagicMock(return_value = 'the-handle')
    poll_ready = mock.MagicMock(return_value = 'ready-value')
    terminate = mock.MagicMock()

    mp = managed_process_generic(launch, poll_ready, terminate)
    self.assertFalse(mp.is_running)

    result = mp.start(timeout_s = 5, interval_s = 0.01)

    self.assertEqual('ready-value', result)
    self.assertEqual('ready-value', mp.ready_value)
    self.assertTrue(mp.is_running)
    launch.assert_called_once()
    poll_ready.assert_called_once()

    mp.stop()
    self.assertFalse(mp.is_running)
    self.assertIsNone(mp.ready_value)
    terminate.assert_called_once_with('the-handle')

  def test_retry_then_ready(self):
    'poll_ready is falsy a few times, then truthy -- start() keeps polling and succeeds.'
    launch = mock.MagicMock(return_value = 'the-handle')
    poll_ready = mock.MagicMock(side_effect = [ False, False, 'ready-value' ])

    mp = managed_process_generic(launch, poll_ready)
    result = mp.start(timeout_s = 5, interval_s = 0.01)

    self.assertEqual('ready-value', result)
    self.assertEqual(3, poll_ready.call_count)

  def test_retry_timeout(self):
    'poll_ready never becomes truthy -- start() raises, but the process is still considered launched.'
    launch = mock.MagicMock(return_value = 'the-handle')
    poll_ready = mock.MagicMock(return_value = False)
    terminate = mock.MagicMock()

    mp = managed_process_generic(launch, poll_ready, terminate)
    with self.assertRaises(system_error):
      mp.start(timeout_s = 0.2, interval_s = 0.05)

    self.assertGreater(poll_ready.call_count, 1)
    # the underlying process really was launched (e.g. a VM that booted but
    # never got an IP) -- is_running stays True until the caller explicitly
    # calls stop(), which must still work after a failed start().
    self.assertTrue(mp.is_running)
    mp.stop()
    self.assertFalse(mp.is_running)
    terminate.assert_called_once_with('the-handle')

  def test_immediate_launch_failure_never_polls(self):
    'launch() raising propagates immediately -- poll_ready is never called.'
    launch = mock.MagicMock(side_effect = RuntimeError('boom'))
    poll_ready = mock.MagicMock()

    mp = managed_process_generic(launch, poll_ready)
    with self.assertRaises(RuntimeError):
      mp.start(timeout_s = 5, interval_s = 0.01)

    poll_ready.assert_not_called()
    self.assertFalse(mp.is_running)

  def test_immediate_launch_failure_real_missing_command(self):
    'A real missing-command failure (not a mock) propagates the same way.'
    missing = system_command_generic('this-command-definitely-does-not-exist-xyz')
    def launch():
      return missing.call_command([])
    poll_ready = mock.MagicMock()

    mp = managed_process_generic(launch, poll_ready)
    with self.assertRaises(Exception):
      mp.start(timeout_s = 5, interval_s = 0.01)

    poll_ready.assert_not_called()
    self.assertFalse(mp.is_running)

  def test_stop_before_start_is_a_noop(self):
    launch = mock.MagicMock()
    poll_ready = mock.MagicMock()
    terminate = mock.MagicMock()

    mp = managed_process_generic(launch, poll_ready, terminate)
    mp.stop()

    launch.assert_not_called()
    terminate.assert_not_called()

  def test_stop_is_idempotent(self):
    launch = mock.MagicMock(return_value = 'the-handle')
    poll_ready = mock.MagicMock(return_value = True)
    terminate = mock.MagicMock()

    mp = managed_process_generic(launch, poll_ready, terminate)
    mp.start(timeout_s = 5, interval_s = 0.01)
    mp.stop()
    mp.stop()

    terminate.assert_called_once()

if __name__ == '__main__':
  unit_test.main()
