#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest.mock as mock

from bes.testing.unit_test import unit_test
from bes.files.rsync.bf_rsync_command import bf_rsync_command, rsync_progress
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

  # parse_progress_line tests

  def test_parse_progress_line_full(self):
    line = '    163577856  93%  110.33MB/s    0:00:01'
    result = bf_rsync_command.parse_progress_line(line, None)
    self.assertIsInstance(result, rsync_progress)
    self.assertEqual('163577856', result.bytes_done)
    self.assertEqual(93, result.percent)
    self.assertEqual('110.33MB/s', result.rate)
    self.assertEqual('0:00:01', result.elapsed)

  def test_parse_progress_line_with_comma_bytes(self):
    line = '  1,048,576  50%  10.00MB/s    0:00:05'
    result = bf_rsync_command.parse_progress_line(line, None)
    self.assertIsNotNone(result)
    self.assertEqual('1,048,576', result.bytes_done)
    self.assertEqual(50, result.percent)

  def test_parse_progress_line_human_readable(self):
    line = '     155.96M  93%  110.33MB/s    0:00:01'
    result = bf_rsync_command.parse_progress_line(line, None)
    self.assertIsNotNone(result)
    self.assertEqual('155.96M', result.bytes_done)
    self.assertEqual(93, result.percent)
    self.assertEqual('110.33MB/s', result.rate)

  def test_parse_progress_line_on_stderr(self):
    line = '     163577856  50%  50.00MB/s    0:00:03'
    result = bf_rsync_command.parse_progress_line(None, line)
    self.assertIsNotNone(result)
    self.assertEqual(50, result.percent)

  def test_parse_progress_line_none_for_non_progress(self):
    self.assertIsNone(bf_rsync_command.parse_progress_line('total size is 175792128', None))
    self.assertIsNone(bf_rsync_command.parse_progress_line('', None))
    self.assertIsNone(bf_rsync_command.parse_progress_line(None, None))
    self.assertIsNone(bf_rsync_command.parse_progress_line('sent 123 bytes  received 45 bytes', None))

  def test_parse_progress_line_final_with_xfr_suffix(self):
    line = '  175792128 100%  110.74MB/s    0:00:01 (xfr#1, to-chk=0/1)'
    result = bf_rsync_command.parse_progress_line(line, None)
    self.assertIsNotNone(result)
    self.assertEqual(100, result.percent)
    self.assertEqual('175792128', result.bytes_done)

if __name__ == '__main__':
  unit_test.main()
