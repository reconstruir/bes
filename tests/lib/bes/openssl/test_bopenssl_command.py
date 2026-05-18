#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.openssl.bopenssl_command import bopenssl_command
from bes.openssl.bopenssl_error import bopenssl_error

class test_bopenssl_command(unit_test):

  # 30
  def test_exe_name(self):
    self.assertEqual('openssl', bopenssl_command.exe_name())

  # 31
  def test_has_command(self):
    result = bopenssl_command.has_command()
    self.assertIsInstance(result, bool)

  # 32
  def test_call_command_not_found(self):
    import unittest.mock as mock
    with mock.patch.object(bopenssl_command, '_find_exe', side_effect=bopenssl_error('not found')):
      with self.assertRaises(bopenssl_error):
        bopenssl_command.call_command(['version'])

if __name__ == '__main__':
  unit_test.main()
