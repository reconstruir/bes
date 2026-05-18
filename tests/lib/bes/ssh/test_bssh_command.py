#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.ssh.bssh_command import bssh_command
from bes.ssh.bssh_error import bssh_error

class test_bssh_command(unit_test):

  # 1
  def test_exe_name(self):
    self.assertEqual('ssh', bssh_command.exe_name())

  # 2
  def test_supported_systems(self):
    self.assertEqual(('linux', 'macos'), bssh_command.supported_systems())

  # 3
  def test_has_command(self):
    result = bssh_command.has_command()
    self.assertIsInstance(result, bool)

  # 4
  def test_call_command_not_found(self):
    import unittest.mock as mock
    with mock.patch.object(bssh_command, '_find_exe', side_effect=bssh_error('not found')):
      with self.assertRaises(bssh_error):
        bssh_command.call_command(['-V'])

if __name__ == '__main__':
  unit_test.main()
