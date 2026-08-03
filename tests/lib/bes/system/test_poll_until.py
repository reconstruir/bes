#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.poll_until import poll_until
from bes.system.system_error import system_error
from bes.testing.unit_test import unit_test

class test_poll_until(unit_test):

  def test_happy_path_returns_immediately(self):
    calls = []
    def predicate():
      calls.append(1)
      return 'ready-value'
    result = poll_until(predicate, timeout_s = 5, interval_s = 0.01)
    self.assertEqual('ready-value', result)
    self.assertEqual(1, len(calls))

  def test_retry_then_ready(self):
    results = [ False, False, 'ready-value' ]
    calls = []
    def predicate():
      calls.append(1)
      return results.pop(0)
    result = poll_until(predicate, timeout_s = 5, interval_s = 0.01)
    self.assertEqual('ready-value', result)
    self.assertEqual(3, len(calls))

  def test_timeout_raises_system_error(self):
    calls = []
    def predicate():
      calls.append(1)
      return False
    with self.assertRaises(system_error):
      poll_until(predicate, timeout_s = 0.2, interval_s = 0.05)
    self.assertGreater(len(calls), 1)

  def test_timeout_message_used(self):
    with self.assertRaises(system_error) as ctx:
      poll_until(lambda: False, timeout_s = 0.05, interval_s = 0.01,
                timeout_message = 'custom timeout message')
    self.assertEqual('custom timeout message', str(ctx.exception))

  def test_predicate_called_at_least_once_even_with_zero_timeout(self):
    calls = []
    def predicate():
      calls.append(1)
      return False
    with self.assertRaises(system_error):
      poll_until(predicate, timeout_s = 0, interval_s = 0.01)
    self.assertEqual(1, len(calls))

if __name__ == '__main__':
  unit_test.main()
