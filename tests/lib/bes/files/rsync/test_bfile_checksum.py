#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import hashlib
import os
import os.path as path
import subprocess
import sys

from bes.testing.unit_test import unit_test
from bes.files.rsync.bf_rsync_file_sync import bf_rsync_file_sync


class test_bfile_checksum(unit_test):

  @classmethod
  def _script_path(clazz):
    return bf_rsync_file_sync._local_checksum_script_path()

  def _run_script(self, *args):
    result = subprocess.run(
      [sys.executable, self._script_path()] + list(args),
      capture_output=True,
      text=True,
    )
    return result

  def _write_file(self, content):
    p = path.join(self.make_temp_dir(), 'testfile.bin')
    with open(p, 'wb') as f:
      f.write(content)
    return p

  # 111
  def test_script_exists(self):
    self.assertTrue(path.isfile(self._script_path()))

  # 112
  def test_missing_file_outputs_missing(self):
    result = self._run_script('/nonexistent/path/file.mp4')
    self.assertEqual(0, result.returncode)
    self.assertIn('sha256: MISSING', result.stdout)

  # 113
  def test_checksum_line_format(self):
    content = b'hello world'
    filepath = self._write_file(content)
    result = self._run_script(filepath)
    self.assertEqual(0, result.returncode)
    lines = [line for line in result.stdout.splitlines() if line.startswith('sha256: CHECKSUM: ')]
    self.assertEqual(1, len(lines))
    hexhash = lines[0][len('sha256: CHECKSUM: '):]
    expected = hashlib.sha256(content).hexdigest()
    self.assertEqual(expected, hexhash)

  # 114
  def test_checksum_matches_hashlib(self):
    content = os.urandom(1024 * 1024)
    filepath = self._write_file(content)
    result = self._run_script(filepath)
    lines = [line for line in result.stdout.splitlines() if line.startswith('sha256: CHECKSUM: ')]
    hexhash = lines[0][len('sha256: CHECKSUM: '):]
    expected = hashlib.sha256(content).hexdigest()
    self.assertEqual(expected, hexhash)

  # 115
  def test_progress_lines_emitted(self):
    content = b'x' * (5 * 1024 * 1024)
    filepath = self._write_file(content)
    result = self._run_script(filepath)
    progress_lines = [line for line in result.stdout.splitlines() if line.startswith('sha256: PROGRESS: ')]
    self.assertGreater(len(progress_lines), 0)

  # 116
  def test_progress_line_format(self):
    content = b'y' * (3 * 1024 * 1024)
    filepath = self._write_file(content)
    result = self._run_script(filepath)
    progress_lines = [line for line in result.stdout.splitlines() if line.startswith('sha256: PROGRESS: ')]
    for line in progress_lines:
      raw = line[len('sha256: PROGRESS: '):]
      parts = raw.split('/')
      self.assertEqual(2, len(parts), f'bad progress line: {line}')
      self.assertTrue(parts[0].isdigit(), f'bytes_done not int: {line}')
      self.assertTrue(parts[1].isdigit(), f'total_bytes not int: {line}')

  # 117
  def test_progress_bytes_done_increases(self):
    content = b'z' * (10 * 1024 * 1024)
    filepath = self._write_file(content)
    result = self._run_script(filepath)
    progress_lines = [line for line in result.stdout.splitlines() if line.startswith('sha256: PROGRESS: ')]
    values = []
    for line in progress_lines:
      raw = line[len('sha256: PROGRESS: '):]
      parts = raw.split('/')
      values.append(int(parts[0]))
    self.assertEqual(values, sorted(values))

  # 118
  def test_progress_total_bytes_consistent(self):
    content = b'w' * (4 * 1024 * 1024)
    filepath = self._write_file(content)
    result = self._run_script(filepath)
    progress_lines = [line for line in result.stdout.splitlines() if line.startswith('sha256: PROGRESS: ')]
    totals = set()
    for line in progress_lines:
      raw = line[len('sha256: PROGRESS: '):]
      parts = raw.split('/')
      totals.add(int(parts[1]))
    self.assertEqual(1, len(totals), f'total_bytes varies across progress lines: {totals}')
    self.assertEqual(len(content), totals.pop())

  # 119
  def test_last_progress_equals_total(self):
    content = b'v' * (2 * 1024 * 1024)
    filepath = self._write_file(content)
    result = self._run_script(filepath)
    progress_lines = [line for line in result.stdout.splitlines() if line.startswith('sha256: PROGRESS: ')]
    last = progress_lines[-1]
    raw = last[len('sha256: PROGRESS: '):]
    parts = raw.split('/')
    self.assertEqual(int(parts[0]), int(parts[1]))

  # 120
  def test_at_most_100_progress_lines_for_large_file(self):
    content = b'u' * (20 * 1024 * 1024)
    filepath = self._write_file(content)
    result = self._run_script(filepath)
    progress_lines = [line for line in result.stdout.splitlines() if line.startswith('sha256: PROGRESS: ')]
    self.assertLessEqual(len(progress_lines), 100)

  # 121
  def test_small_file_has_checksum_line(self):
    filepath = self._write_file(b'tiny')
    result = self._run_script(filepath)
    self.assertIn('sha256: CHECKSUM: ', result.stdout)
    self.assertNotIn('sha256: MISSING', result.stdout)

  # 122
  def test_checksum_line_appears_after_all_progress_lines(self):
    content = b'q' * (3 * 1024 * 1024)
    filepath = self._write_file(content)
    result = self._run_script(filepath)
    lines = result.stdout.splitlines()
    checksum_index = next(
      (i for i, l in enumerate(lines) if l.startswith('sha256: CHECKSUM: ')),
      None,
    )
    self.assertIsNotNone(checksum_index)
    for i, line in enumerate(lines):
      if line.startswith('sha256: PROGRESS: '):
        self.assertLess(i, checksum_index, 'PROGRESS line appears after CHECKSUM line')

  # 123
  def test_empty_file_has_checksum_line(self):
    filepath = self._write_file(b'')
    result = self._run_script(filepath)
    lines = [l for l in result.stdout.splitlines() if l.startswith('sha256: CHECKSUM: ')]
    self.assertEqual(1, len(lines))
    hexhash = lines[0][len('sha256: CHECKSUM: '):]
    self.assertEqual(hashlib.sha256(b'').hexdigest(), hexhash)


if __name__ == '__main__':
  unit_test.main()
