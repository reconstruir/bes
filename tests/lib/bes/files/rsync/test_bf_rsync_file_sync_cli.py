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

  def _capture_kwargs(self, extra_args):
    'Run the CLI with extra_args and return the kwargs passed to bf_rsync_file_sync.__init__.'
    tmp_key = self.make_temp_file()
    tmp_dir = self.make_temp_dir()
    captured = []
    def capture_init(self_inner, ssh_key, destination, source_dirs, **kwargs):
      captured.append(kwargs)
      raise SystemExit(0)
    with mock.patch.object(bf_rsync_file_sync, '__init__', capture_init):
      with mock.patch('sys.argv', ['bfile-sync', tmp_key, 'nas2:/dest', tmp_dir] + extra_args):
        try:
          bf_rsync_file_sync_cli.run()
        except SystemExit:
          pass
    return captured[0] if captured else None

  def test_cli_min_size_parsed_and_passed(self):
    kwargs = self._capture_kwargs(['--min-size', '10M'])
    self.assertEqual(10 * 1024 ** 2, kwargs['min_size'])

  def test_cli_max_size_parsed_and_passed(self):
    kwargs = self._capture_kwargs(['--max-size', '2G'])
    self.assertEqual(2 * 1024 ** 3, kwargs['max_size'])

  def test_cli_mime_type_passed(self):
    kwargs = self._capture_kwargs(['--mime-type', 'video/*'])
    self.assertEqual('video/*', kwargs['mime_type'])

  def test_cli_no_size_filters_defaults_to_none(self):
    kwargs = self._capture_kwargs([])
    self.assertIsNone(kwargs['min_size'])
    self.assertIsNone(kwargs['max_size'])

  def test_cli_no_mime_type_defaults_to_none(self):
    kwargs = self._capture_kwargs([])
    self.assertIsNone(kwargs['mime_type'])

  def test_cli_invalid_min_size_exits_with_error(self):
    code = self._run_cli_with_key(['--min-size', 'notasize'])
    self.assertNotEqual(0, code)

  def test_cli_invalid_max_size_exits_with_error(self):
    code = self._run_cli_with_key(['--max-size', 'bad'])
    self.assertNotEqual(0, code)

  def _run_cli_with_key(self, extra_args):
    tmp_key = self.make_temp_file()
    tmp_dir = self.make_temp_dir()
    with mock.patch('sys.argv', ['bfile-sync', tmp_key, 'nas2:/dest', tmp_dir] + extra_args):
      with self.assertRaises(SystemExit) as ctx:
        bf_rsync_file_sync_cli.run()
    return ctx.exception.code

if __name__ == '__main__':
  unit_test.main()
