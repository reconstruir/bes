#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest.mock as mock

from bes.testing.unit_test import unit_test
from bes.files.rsync.bf_rsync_command import bf_rsync_command
from bes.files.rsync.bf_rsync_error import bf_rsync_error

class test_bf_rsync_command(unit_test):

  # 41
  def test_exe_name(self):
    self.assertEqual('rsync', bf_rsync_command.exe_name())

  # 42
  def test_supported_systems(self):
    self.assertEqual(('linux', 'macos'), bf_rsync_command.supported_systems())

  # 43
  def test_has_command(self):
    result = bf_rsync_command.has_command()
    self.assertIsInstance(result, bool)

  # 44
  def test_call_command_not_found(self):
    with mock.patch.object(bf_rsync_command, '_find_exe', side_effect=bf_rsync_error('not found')):
      with self.assertRaises(bf_rsync_error):
        bf_rsync_command.call_command(['--version'])

if __name__ == '__main__':
  unit_test.main()
