#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import sys
import unittest.mock as mock

from bes.testing.unit_test import unit_test
from bes.files.rsync.bf_rsync_file_sync import bf_rsync_file_sync
from bes.files.rsync.bf_rsync_file_sync_cli import bf_rsync_file_sync_cli
from bes.files.rsync.bf_rsync_error import bf_rsync_error

class test_bf_rsync_file_sync_cli(unit_test):

  def _run_cli(self, args):
    with mock.patch('sys.argv', ['bfile-sync'] + args):
      with self.assertRaises(SystemExit) as ctx:
        bf_rsync_file_sync_cli.run()
    return ctx.exception.code

  # 87
  def test_cli_missing_ssh_key_arg(self):
    code = self._run_cli([])
    self.assertNotEqual(0, code)

  # 88
  def test_cli_missing_destination_arg(self):
    code = self._run_cli(['key'])
    self.assertNotEqual(0, code)

  # 89
  def test_cli_missing_source_dir_arg(self):
    code = self._run_cli(['key', 'nas2:/mnt/stuff/p'])
    self.assertNotEqual(0, code)

  # 90
  def test_cli_invalid_destination_format(self):
    tmp_key = self.make_temp_file()
    tmp_dir = self.make_temp_dir()
    with self.assertRaises((SystemExit, bf_rsync_error, Exception)):
      with mock.patch('sys.argv', ['bfile-sync', tmp_key, 'no-colon-here', tmp_dir]):
        bf_rsync_file_sync_cli.run()

  # 91
  def test_cli_nonexistent_ssh_key(self):
    tmp_dir = self.make_temp_dir()
    with self.assertRaises((SystemExit, bf_rsync_error, Exception)):
      with mock.patch('sys.argv', ['bfile-sync', '/nonexistent/key', 'nas2:/mnt', tmp_dir]):
        bf_rsync_file_sync_cli.run()

  # 92
  def test_cli_passes_args_to_file_sync(self):
    tmp_key = self.make_temp_file()
    tmp_dir = self.make_temp_dir()
    created = []
    real_init = bf_rsync_file_sync.__init__
    def capture_init(self, ssh_key, destination, source_dirs, **kwargs):
      created.append((ssh_key, destination, source_dirs))
      raise SystemExit(0)
    with mock.patch.object(bf_rsync_file_sync, '__init__', capture_init):
      with mock.patch('sys.argv', ['bfile-sync', tmp_key, 'nas2:/dest', tmp_dir]):
        try:
          bf_rsync_file_sync_cli.run()
        except SystemExit:
          pass
    self.assertEqual(1, len(created))
    self.assertIn(tmp_key, created[0][0])
    self.assertEqual('nas2:/dest', created[0][1])

  # 93
  def test_cli_multiple_source_dirs(self):
    tmp_key = self.make_temp_file()
    dir1 = self.make_temp_dir()
    dir2 = self.make_temp_dir()
    created = []
    def capture_init(self, ssh_key, destination, source_dirs, **kwargs):
      created.append(source_dirs)
      raise SystemExit(0)
    with mock.patch.object(bf_rsync_file_sync, '__init__', capture_init):
      with mock.patch('sys.argv', ['bfile-sync', tmp_key, 'nas2:/dest', dir1, dir2]):
        try:
          bf_rsync_file_sync_cli.run()
        except SystemExit:
          pass
    self.assertEqual(1, len(created))
    self.assertEqual(2, len(created[0]))

if __name__ == '__main__':
  unit_test.main()
