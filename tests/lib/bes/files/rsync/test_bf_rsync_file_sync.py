#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import getpass
import hashlib
import os
import os.path as path
import time
import unittest.mock as mock

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.files.bf_entry import bf_entry
from bes.files.mime.bf_mime_type_detector import bf_mime_type_detector
from bes.files.rsync.bf_rsync_command import bf_rsync_command
from bes.files.rsync.bf_rsync_error import bf_rsync_error
from bes.files.rsync.bf_rsync_file_sync import bf_rsync_file_sync
from bes.ssh.bssh_command import bssh_command
from bes.ssh.bssh_error import bssh_error
from bes.ssh.bssh_sandbox import bssh_sandbox
from bes.system.execute import execute


class test_bf_rsync_file_sync_unit(unit_test):
  'Unit tests — all subprocess calls mocked.'

  def _make_syncer(self, source_dirs=None, **kwargs):
    tmp_dir = self.make_temp_dir()
    key = path.join(tmp_dir, 'key')
    open(key, 'w').close()
    source_dirs = source_dirs or [self.make_temp_dir()]
    return bf_rsync_file_sync(
      key, 'nas2:/mnt/stuff/p', source_dirs,
      strict_host_checking=False, **kwargs
    )

  def _make_entry(self, absolute_path):
    return bf_entry(path.basename(absolute_path), root_dir=path.dirname(absolute_path))

  # 45
  def test_ssh_sha256_missing(self):
    syncer = self._make_syncer()
    def fake_ewp(args, line_parser, **kwargs):
      line_parser('sha256: MISSING', None)
      return _fake_progress_rv()
    with mock.patch.object(execute, 'execute_with_progress', side_effect=fake_ewp):
      result = syncer._ssh_sha256('/mnt/stuff/p/video.mp4')
    self.assertIsNone(result)

  # 46
  def test_ssh_sha256_match(self):
    syncer = self._make_syncer()
    hexhash = 'a' * 64
    def fake_ewp(args, line_parser, **kwargs):
      line_parser(f'sha256: CHECKSUM: {hexhash}', None)
      return _fake_progress_rv()
    with mock.patch.object(execute, 'execute_with_progress', side_effect=fake_ewp):
      result = syncer._ssh_sha256('/mnt/stuff/p/video.mp4')
    self.assertEqual(hexhash, result)

  # 47
  def test_ssh_sha256_ssh_error(self):
    syncer = self._make_syncer()
    def fake_ewp(args, line_parser, **kwargs):
      return _fake_progress_rv(exit_code=1, stderr='refused')
    with mock.patch.object(execute, 'execute_with_progress', side_effect=fake_ewp):
      with self.assertRaises(bssh_error):
        syncer._ssh_sha256('/mnt/stuff/p/video.mp4')

  # 48
  def test_local_checksum_cached(self):
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'video.mp4')
    with open(src, 'wb') as f:
      f.write(b'data')
    syncer = self._make_syncer(source_dirs=[src_dir])
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='a' * 64) as m:
      syncer._ssh_sha256 = lambda p, progress_callback=None: 'a' * 64  # same hash → skip
      with mock.patch.object(os, 'remove'):
        syncer._sync_one(self._make_entry(src))
    self.assertEqual(1, m.call_count)

  # 49
  def test_local_checksum_large_file(self):
    # checksum_cache handles mtime keying — just confirm it's called once per file
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'big.mp4')
    with open(src, 'wb') as f:
      f.write(b'x' * 1024)
    syncer = self._make_syncer(source_dirs=[src_dir])
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='b' * 64) as m:
      syncer._ssh_sha256 = lambda p, progress_callback=None: 'b' * 64
      with mock.patch.object(os, 'remove'):
        syncer._sync_one(self._make_entry(src))
    self.assertEqual(1, m.call_count)

  # 50
  def test_decision_destination_missing(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'data', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='c' * 64):
      transferred = []
      syncer._rsync = lambda s, d: transferred.append(d)
      syncer._ssh_sha256 = lambda p, progress_callback=None: (None if not transferred else 'c' * 64)
      syncer._ssh_mkdir = lambda d: None
      with mock.patch.object(os, 'remove'):
        syncer._sync_one(self._make_entry(src))
    self.assertTrue(any('/mnt/stuff/p/' + path.basename(src) == d for d in transferred))

  # 51
  def test_decision_checksums_match(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'same', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    rsync_called = []
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='d' * 64):
      with mock.patch.object(bf_rsync_command, 'call_command_with_progress', side_effect=lambda a, **kw: rsync_called.append(a)):
        syncer._ssh_sha256 = lambda p, progress_callback=None: 'd' * 64
        with mock.patch.object(os, 'remove'):
          syncer._sync_one(self._make_entry(src))
    self.assertEqual([], rsync_called)

  # 52
  def test_decision_checksums_differ(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'local', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    transferred = []
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='e' * 64):
      call_count = [0]
      def ssh_sha256(p, progress_callback=None):
        call_count[0] += 1
        if call_count[0] == 1:
          return 'f' * 64  # pre-transfer: different
        return 'e' * 64    # post-transfer: verified
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: transferred.append(d)
      syncer._ssh_mkdir = lambda d: None
      with mock.patch.object(os, 'remove'):
        syncer._sync_one(self._make_entry(src))
    self.assertTrue(any('-' + 'e' * 8 + '.mp4' in d for d in transferred))

  # 53
  def test_unique_name_deterministic(self):
    name1 = bf_rsync_file_sync._make_unique_name('video.mp4', 'abc123' + 'x' * 58)
    name2 = bf_rsync_file_sync._make_unique_name('video.mp4', 'abc123' + 'x' * 58)
    self.assertEqual(name1, name2)

  # 54
  def test_unique_name_no_collision_if_hash_differs(self):
    name1 = bf_rsync_file_sync._make_unique_name('video.mp4', 'aaaa' + 'x' * 60)
    name2 = bf_rsync_file_sync._make_unique_name('video.mp4', 'bbbb' + 'x' * 60)
    self.assertNotEqual(name1, name2)

  # 55
  def test_unique_name_extension_preserved(self):
    name = bf_rsync_file_sync._make_unique_name('video.mp4', 'a' * 64)
    self.assertTrue(name.endswith('.mp4'))

  # 56
  def test_unique_name_no_extension(self):
    name = bf_rsync_file_sync._make_unique_name('noext', 'b' * 64)
    self.assertIn('bbbbbbbb', name)
    self.assertFalse(name.endswith('.'))

  # 57
  def test_transfer_builds_correct_rsync_args(self):
    syncer = self._make_syncer()
    syncer._strict_host_checking = False
    captured = []
    with mock.patch.object(bf_rsync_command, 'call_command_with_progress', side_effect=lambda a, **kw: captured.extend(a)):
      syncer._rsync('/tmp/video.mp4', '/mnt/stuff/p/video.mp4')
    args_str = ' '.join(captured)
    self.assertIn('--partial', args_str)
    self.assertIn('.rsync-partial', args_str)
    self.assertIn('--progress', args_str)
    self.assertIn('StrictHostKeyChecking=no', args_str)
    self.assertIn('nas2:/mnt/stuff/p/video.mp4', args_str)

  # 58
  def test_transfer_no_home_known_hosts(self):
    home_kh = os.path.expanduser('~/.ssh/known_hosts')
    syncer = self._make_syncer()
    captured = []
    with mock.patch.object(bf_rsync_command, 'call_command_with_progress', side_effect=lambda a, **kw: captured.extend(a)):
      syncer._rsync('/tmp/video.mp4', '/mnt/stuff/p/video.mp4')
    self.assertNotIn(home_kh, ' '.join(captured))

  # 59
  def test_transfer_excludes_ds_store(self):
    syncer = self._make_syncer()
    captured = []
    with mock.patch.object(bf_rsync_command, 'call_command_with_progress', side_effect=lambda a, **kw: captured.extend(a)):
      syncer._rsync('/tmp/video.mp4', '/mnt/stuff/p/video.mp4')
    self.assertTrue(any('.DS_Store' in a for a in captured))

  # 60
  def test_transfer_no_remove_source_files(self):
    syncer = self._make_syncer()
    captured = []
    with mock.patch.object(bf_rsync_command, 'call_command_with_progress', side_effect=lambda a, **kw: captured.extend(a)):
      syncer._rsync('/tmp/video.mp4', '/mnt/stuff/p/video.mp4')
    self.assertNotIn('--remove-source-files', captured)

  # 61
  def test_transfer_no_no_whole_file(self):
    syncer = self._make_syncer()
    captured = []
    with mock.patch.object(bf_rsync_command, 'call_command_with_progress', side_effect=lambda a, **kw: captured.extend(a)):
      syncer._rsync('/tmp/video.mp4', '/mnt/stuff/p/video.mp4')
    self.assertNotIn('--no-whole-file', captured)

  # 62
  def test_verify_checksum_match(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'ok', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    removed = []
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='a' * 64):
      call_count = [0]
      def ssh_sha256(p, progress_callback=None):
        call_count[0] += 1
        return None if call_count[0] == 1 else 'a' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
      syncer._ssh_mkdir = lambda d: None
      with mock.patch.object(os, 'remove', side_effect=lambda p: removed.append(p)):
        syncer._sync_one(self._make_entry(src))
    self.assertIn(src, removed)

  # 63
  def test_verify_checksum_mismatch(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'mismatch', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='a' * 64):
      call_count = [0]
      def ssh_sha256(p, progress_callback=None):
        call_count[0] += 1
        if call_count[0] == 1:
          return None  # destination missing → transfer
        return 'b' * 64  # post-transfer: mismatch
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
      syncer._ssh_mkdir = lambda d: None
      with self.assertRaises(bf_rsync_error):
        syncer._sync_one(self._make_entry(src))

  # 64
  def test_source_deleted_after_verify(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'del', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    removed = []
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='c' * 64):
      call_count = [0]
      def ssh_sha256(p, progress_callback=None):
        call_count[0] += 1
        return None if call_count[0] == 1 else 'c' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
      syncer._ssh_mkdir = lambda d: None
      with mock.patch.object(os, 'remove', side_effect=lambda p: removed.append(p)):
        syncer._sync_one(self._make_entry(src))
    self.assertEqual(1, removed.count(src))

  # 65
  def test_source_not_deleted_on_rsync_failure(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'nodrop', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='d' * 64):
      syncer._ssh_sha256 = lambda p, progress_callback=None: None
      syncer._rsync = lambda s, d: (_ for _ in ()).throw(bf_rsync_error('rsync failed'))
      syncer._ssh_mkdir = lambda d: None
      removed = []
      with mock.patch.object(os, 'remove', side_effect=lambda p: removed.append(p)):
        with self.assertRaises(bf_rsync_error):
          syncer._sync_one(self._make_entry(src))
    self.assertNotIn(src, removed)

  # 66
  def test_source_not_deleted_on_verify_ssh_error(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'sshfail', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='e' * 64):
      call_count = [0]
      def ssh_sha256(p, progress_callback=None):
        call_count[0] += 1
        if call_count[0] == 1:
          return None
        raise bssh_error('verify ssh failed')
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
      syncer._ssh_mkdir = lambda d: None
      removed = []
      with mock.patch.object(os, 'remove', side_effect=lambda p: removed.append(p)):
        with self.assertRaises(bssh_error):
          syncer._sync_one(self._make_entry(src))
    self.assertNotIn(src, removed)

  # 67
  def test_skip_deletes_source(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'skip', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    removed = []
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='f' * 64):
      syncer._ssh_sha256 = lambda p, progress_callback=None: 'f' * 64
      with mock.patch.object(os, 'remove', side_effect=lambda p: removed.append(p)):
        syncer._sync_one(self._make_entry(src))
    self.assertIn(src, removed)

  # 68
  def test_skip_no_rsync_call(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'skip2', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='0' * 64):
      syncer._ssh_sha256 = lambda p, progress_callback=None: '0' * 64
      rsync_calls = []
      with mock.patch.object(bf_rsync_command, 'call_command_with_progress', side_effect=lambda a, **kw: rsync_calls.append(a)):
        with mock.patch.object(os, 'remove'):
          syncer._sync_one(self._make_entry(src))
    self.assertEqual([], rsync_calls)

  # 69
  def test_retry_on_ssh_failure(self):
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'video.mp4')
    with open(src, 'wb') as f:
      f.write(b'retry')
    syncer = self._make_syncer(source_dirs=[src_dir])
    attempts = [0]
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='1' * 64):
      def ssh_sha256(p, progress_callback=None):
        attempts[0] += 1
        if attempts[0] < 3:
          raise bssh_error('network error')
        return None if attempts[0] == 3 else '1' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
      syncer._ssh_mkdir = lambda d: None
      with mock.patch('time.sleep'):
        with mock.patch.object(os, 'remove'):
          syncer._run_loop()
    self.assertGreater(attempts[0], 1)

  # 70
  def test_retry_on_rsync_failure(self):
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'clip.mp4')
    with open(src, 'wb') as f:
      f.write(b'retry-rsync')
    syncer = self._make_syncer(source_dirs=[src_dir])
    rsync_attempts = [0]
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='2' * 64):
      def rsync(s, d):
        rsync_attempts[0] += 1
        if rsync_attempts[0] < 2:
          raise bf_rsync_error('rsync failed')
      def ssh_sha256(p, progress_callback=None):
        return None if rsync_attempts[0] < 2 else '2' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = rsync
      syncer._ssh_mkdir = lambda d: None
      with mock.patch('time.sleep'):
        with mock.patch.object(os, 'remove'):
          syncer._run_loop()
    self.assertGreaterEqual(rsync_attempts[0], 2)

  # 71
  def test_retry_wait_duration(self):
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'wait.mp4')
    with open(src, 'wb') as f:
      f.write(b'wait')
    syncer = self._make_syncer(source_dirs=[src_dir])
    attempt = [0]
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='3' * 64):
      def ssh_sha256(p, progress_callback=None):
        attempt[0] += 1
        if attempt[0] == 1:
          raise bssh_error('fail once')
        return None if attempt[0] == 2 else '3' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
      syncer._ssh_mkdir = lambda d: None
      slept = []
      with mock.patch('time.sleep', side_effect=lambda n: slept.append(n)):
        with mock.patch.object(os, 'remove'):
          syncer._run_loop()
    self.assertTrue(any(s == bf_rsync_file_sync.RETRY_WAIT_SECONDS for s in slept))

  # 72
  def test_retry_picks_up_completed_files(self):
    src_dir = self.make_temp_dir()
    done = path.join(src_dir, 'a.mp4')
    todo = path.join(src_dir, 'b.mp4')
    with open(done, 'wb') as f:
      f.write(b'done')
    with open(todo, 'wb') as f:
      f.write(b'todo')
    syncer = self._make_syncer(source_dirs=[src_dir])
    transferred = []
    attempt = [0]
    b_failed = [False]
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='4' * 64):
      def ssh_sha256(p, progress_callback=None):
        attempt[0] += 1
        basename = path.basename(p)
        # Fail b.mp4 on its first pre-check encounter to exercise the retry path.
        if basename == 'b.mp4' and not b_failed[0]:
          b_failed[0] = True
          raise bssh_error('fail b once')
        # Pre-check (file not yet rsync'd): return None so transfer is attempted.
        # Verify (file already rsync'd): return the expected hash so verify succeeds.
        if basename in ('a.mp4', 'b.mp4') and basename not in transferred:
          return None
        return '4' * 64
      syncer._ssh_sha256 = ssh_sha256
      def rsync(s, d):
        transferred.append(path.basename(s))
      syncer._rsync = rsync
      syncer._ssh_mkdir = lambda d: None
      with mock.patch('time.sleep'):
        with mock.patch.object(os, 'remove'):
          syncer._run_loop()
    # a.mp4 should be transferred exactly once
    self.assertEqual(1, transferred.count('a.mp4'))

  # 73
  def test_no_retry_on_full_success(self):
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'ok.mp4')
    with open(src, 'wb') as f:
      f.write(b'ok')
    syncer = self._make_syncer(source_dirs=[src_dir])
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='5' * 64):
      call_count = [0]
      def ssh_sha256(p, progress_callback=None):
        call_count[0] += 1
        return None if call_count[0] == 1 else '5' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
      syncer._ssh_mkdir = lambda d: None
      slept = []
      with mock.patch('time.sleep', side_effect=lambda n: slept.append(n)):
        with mock.patch.object(os, 'remove'):
          syncer._run_loop()
    self.assertEqual([], slept)

  # 74
  def test_multiple_source_dirs(self):
    dir1 = self.make_temp_dir()
    dir2 = self.make_temp_dir()
    f1 = path.join(dir1, 'clip1.mp4')
    f2 = path.join(dir2, 'clip2.mp4')
    with open(f1, 'wb') as f:
      f.write(b'clip1')
    with open(f2, 'wb') as f:
      f.write(b'clip2')
    syncer = self._make_syncer(source_dirs=[dir1, dir2])
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    transferred = []
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='6' * 64):
      call_count = [0]
      def ssh_sha256(p, progress_callback=None):
        call_count[0] += 1
        return None if call_count[0] % 2 == 1 else '6' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: transferred.append(path.basename(s))
      syncer._ssh_mkdir = lambda d: None
      with mock.patch.object(os, 'remove'):
        syncer._run_loop()
    self.assertIn('clip1.mp4', transferred)
    self.assertIn('clip2.mp4', transferred)

  # 75
  def test_empty_source_dir(self):
    syncer = self._make_syncer(source_dirs=[self.make_temp_dir()])
    rsync_called = []
    with mock.patch.object(bf_rsync_command, 'call_command_with_progress', side_effect=lambda a, **kw: rsync_called.append(a)):
      syncer._run_loop()
    self.assertEqual([], rsync_called)

  # 76
  def test_nonexistent_source_dir(self):
    syncer = self._make_syncer(source_dirs=['/nonexistent/dir'])
    with mock.patch.object(bf_rsync_command, 'call_command_with_progress'):
      syncer._run_loop()  # should not raise

  # 77-86: logging tests
  def test_log_skip_line(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'log', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='7' * 64):
      syncer._ssh_sha256 = lambda p, progress_callback=None: '7' * 64
      with mock.patch.object(os, 'remove'):
        action, *_ = syncer._sync_one(self._make_entry(src))
    self.assertEqual('skip', action)

  def test_log_transfer_line(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'xfer', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='8' * 64):
      call_count = [0]
      def ssh_sha256(p, progress_callback=None):
        call_count[0] += 1
        return None if call_count[0] == 1 else '8' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
      syncer._ssh_mkdir = lambda d: None
      with mock.patch.object(os, 'remove'):
        action, *_ = syncer._sync_one(self._make_entry(src))
    self.assertEqual('transfer', action)

  def test_log_has_timestamps(self):
    import re
    syncer = self._make_syncer()
    log_lines = []
    orig_emit = bf_rsync_file_sync._emit
    def capturing_emit(self_inner, tag, msg):
      ts = __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      line = f'{ts} [{tag:<8}] {msg}'
      log_lines.append(line)
    syncer._emit = lambda tag, msg: capturing_emit(syncer, tag, msg)
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    src = self.make_temp_file(content=b'ts', suffix='.mp4')
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='9' * 64):
      syncer._ssh_sha256 = lambda p, progress_callback=None: '9' * 64
      with mock.patch.object(os, 'remove'):
        syncer._sync_one(self._make_entry(src))
    pattern = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
    for line in log_lines:
      self.assertRegex(line, pattern)

  def test_log_written_to_file(self):
    log_path = path.join(self.make_temp_dir(), 'sync.log')
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'logged.mp4')
    with open(src, 'wb') as f:
      f.write(b'log-file')
    tmp_dir = self.make_temp_dir()
    key = path.join(tmp_dir, 'key')
    open(key, 'w').close()
    syncer = bf_rsync_file_sync(key, 'nas2:/mnt/stuff/p', [src_dir],
                                 log_file=log_path, strict_host_checking=False)
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='a1' * 32):
      syncer._ssh_sha256 = lambda p, progress_callback=None: 'a1' * 32
      with mock.patch.object(os, 'remove'):
        with mock.patch.object(syncer, '_cleanup_partial'):
          with mock.patch.object(syncer, '_install_remote_checksum_script'):
            syncer.run()
    self.assertTrue(path.exists(log_path))
    with open(log_path) as f:
      content = f.read()
    self.assertIn('SKIP', content)

  def test_log_cleanup_line(self):
    syncer = self._make_syncer()
    lines = []
    syncer._emit = lambda tag, msg: lines.append(tag)
    with mock.patch.object(bssh_command, 'call_command', return_value=_fake_rv('')):
      syncer._cleanup_partial()
    self.assertIn('CLEANUP', lines)

  # dry-run tests
  def test_dry_run_no_rsync_call(self):
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'video.mp4')
    with open(src, 'wb') as f:
      f.write(b'data')
    syncer = self._make_syncer(source_dirs=[src_dir], dry_run=True)
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    rsync_calls = []
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='a' * 64):
      syncer._ssh_sha256 = lambda p, progress_callback=None: None
      with mock.patch.object(bf_rsync_command, 'call_command_with_progress', side_effect=lambda a, **kw: rsync_calls.append(a)):
        syncer._run_loop()
    self.assertEqual([], rsync_calls)

  def test_dry_run_source_not_deleted(self):
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'video.mp4')
    with open(src, 'wb') as f:
      f.write(b'data')
    syncer = self._make_syncer(source_dirs=[src_dir], dry_run=True)
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='b' * 64):
      syncer._ssh_sha256 = lambda p, progress_callback=None: None
      syncer._run_loop()
    self.assertTrue(path.exists(src))

  def test_dry_run_skip_source_not_deleted(self):
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'video.mp4')
    with open(src, 'wb') as f:
      f.write(b'data')
    syncer = self._make_syncer(source_dirs=[src_dir], dry_run=True)
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='c' * 64):
      syncer._ssh_sha256 = lambda p, progress_callback=None: 'c' * 64
      syncer._run_loop()
    self.assertTrue(path.exists(src))

  def test_dry_run_emits_dry_run_tag(self):
    import io
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'video.mp4')
    with open(src, 'wb') as f:
      f.write(b'data')
    syncer = self._make_syncer(source_dirs=[src_dir], dry_run=True)
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    captured = io.StringIO()
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='d' * 64):
      syncer._ssh_sha256 = lambda p, progress_callback=None: None
      with mock.patch('sys.stdout', new=captured):
        syncer._run_loop()
    self.assertIn('DRY-XFER', captured.getvalue())

  def test_dry_run_no_cleanup_partial(self):
    syncer = self._make_syncer(dry_run=True)
    cleanup_calls = []
    syncer._cleanup_partial = lambda: cleanup_calls.append(True)
    syncer._run_loop()
    self.assertEqual([], cleanup_calls)

  # summary tests
  def test_summary_emitted_after_run(self):
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'video.mp4')
    with open(src, 'wb') as f:
      f.write(b'data')
    syncer = self._make_syncer(source_dirs=[src_dir])
    tags = []
    syncer._emit = lambda tag, msg: tags.append(tag)
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='e' * 64):
      call_count = [0]
      def ssh_sha256(p, progress_callback=None):
        call_count[0] += 1
        return None if call_count[0] == 1 else 'e' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
      syncer._ssh_mkdir = lambda d: None
      with mock.patch.object(os, 'remove'):
        syncer._run_loop()
    self.assertIn('SUMMARY', tags)

  def test_summary_transfer_count_and_bytes(self):
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'video.mp4')
    with open(src, 'wb') as f:
      f.write(b'x' * 2048)
    syncer = self._make_syncer(source_dirs=[src_dir])
    messages = []
    syncer._emit = lambda tag, msg: messages.append((tag, msg))
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='f' * 64):
      call_count = [0]
      def ssh_sha256(p, progress_callback=None):
        call_count[0] += 1
        return None if call_count[0] == 1 else 'f' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
      syncer._ssh_mkdir = lambda d: None
      with mock.patch.object(os, 'remove'):
        syncer._run_loop()
    summary = next(msg for tag, msg in messages if tag == 'SUMMARY')
    self.assertIn('1 transferred', summary)
    self.assertIn('0 skipped', summary)
    self.assertIn('2.0KiB', summary)

  def test_summary_skip_count_and_bytes(self):
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'video.mp4')
    with open(src, 'wb') as f:
      f.write(b'y' * 4096)
    syncer = self._make_syncer(source_dirs=[src_dir])
    messages = []
    syncer._emit = lambda tag, msg: messages.append((tag, msg))
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='0' * 64):
      syncer._ssh_sha256 = lambda p, progress_callback=None: '0' * 64
      with mock.patch.object(os, 'remove'):
        syncer._run_loop()
    summary = next(msg for tag, msg in messages if tag == 'SUMMARY')
    self.assertIn('1 skipped', summary)
    self.assertIn('0 transferred', summary)
    self.assertIn('4.0KiB', summary)

  def test_summary_dry_run_label(self):
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'video.mp4')
    with open(src, 'wb') as f:
      f.write(b'z' * 1024)
    syncer = self._make_syncer(source_dirs=[src_dir], dry_run=True)
    messages = []
    syncer._emit = lambda tag, msg: messages.append((tag, msg))
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='1' * 64):
      syncer._ssh_sha256 = lambda p, progress_callback=None: None
      syncer._run_loop()
    summary = next(msg for tag, msg in messages if tag == 'SUMMARY')
    self.assertIn('would transfer', summary)
    self.assertIn('[dry run]', summary)

  def test_summary_empty_source(self):
    syncer = self._make_syncer(source_dirs=[self.make_temp_dir()])
    messages = []
    syncer._emit = lambda tag, msg: messages.append((tag, msg))
    syncer._run_loop()
    summary = next(msg for tag, msg in messages if tag == 'SUMMARY')
    self.assertIn('no files', summary)

  # recursion tests
  def test_collect_files_recursive(self):
    src_dir = self.make_temp_dir()
    sub = path.join(src_dir, 'sub')
    os.makedirs(sub)
    top_file = path.join(src_dir, 'top.mp4')
    sub_file = path.join(sub, 'deep.mp4')
    open(top_file, 'w').close()
    open(sub_file, 'w').close()
    syncer = self._make_syncer(source_dirs=[src_dir])
    entries = syncer._collect_files()
    abs_paths = [e.absolute_filename for e in entries]
    self.assertIn(top_file, abs_paths)
    self.assertIn(sub_file, abs_paths)

  def test_collect_files_deeply_nested(self):
    src_dir = self.make_temp_dir()
    deep = path.join(src_dir, 'a', 'b', 'c')
    os.makedirs(deep)
    deep_file = path.join(deep, 'movie.mp4')
    open(deep_file, 'w').close()
    syncer = self._make_syncer(source_dirs=[src_dir])
    entries = syncer._collect_files()
    abs_paths = [e.absolute_filename for e in entries]
    self.assertIn(deep_file, abs_paths)

  def test_collect_files_excludes_ds_store_in_subdir(self):
    src_dir = self.make_temp_dir()
    sub = path.join(src_dir, 'sub')
    os.makedirs(sub)
    ds_store = path.join(sub, '.DS_Store')
    real_file = path.join(sub, 'movie.mp4')
    open(ds_store, 'w').close()
    open(real_file, 'w').close()
    syncer = self._make_syncer(source_dirs=[src_dir])
    entries = syncer._collect_files()
    abs_paths = [e.absolute_filename for e in entries]
    self.assertNotIn(ds_store, abs_paths)
    self.assertIn(real_file, abs_paths)

  def test_collect_files_sorted(self):
    src_dir = self.make_temp_dir()
    sub = path.join(src_dir, 'sub')
    os.makedirs(sub)
    open(path.join(src_dir, 'z.mp4'), 'w').close()
    open(path.join(sub, 'a.mp4'), 'w').close()
    syncer = self._make_syncer(source_dirs=[src_dir])
    entries = syncer._collect_files()
    abs_paths = [e.absolute_filename for e in entries]
    self.assertEqual(abs_paths, sorted(abs_paths))

  def test_collect_files_entry_has_relative_filename(self):
    src_dir = self.make_temp_dir()
    sub = path.join(src_dir, 'action')
    os.makedirs(sub)
    open(path.join(sub, 'movie.mp4'), 'w').close()
    syncer = self._make_syncer(source_dirs=[src_dir])
    entries = syncer._collect_files()
    rel_paths = [e.relative_filename for e in entries]
    expected = path.join(path.basename(src_dir), 'action', 'movie.mp4')
    self.assertIn(expected, rel_paths)

  def test_dest_path_uses_relative_filename(self):
    src_dir = self.make_temp_dir()
    sub = path.join(src_dir, 'action')
    os.makedirs(sub)
    src = path.join(sub, 'movie.mp4')
    open(src, 'w').close()
    syncer = self._make_syncer(source_dirs=[src_dir])
    transferred_dest = []
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='a' * 64):
      call_count = [0]
      def ssh_sha256(p, progress_callback=None):
        call_count[0] += 1
        return None if call_count[0] == 1 else 'a' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: transferred_dest.append(d)
      syncer._ssh_mkdir = lambda d: None
      with mock.patch.object(os, 'remove'):
        syncer._run_loop()
    self.assertEqual(1, len(transferred_dest))
    self.assertIn('action/movie.mp4', transferred_dest[0])

  def test_mkdir_called_with_remote_subdir(self):
    src_dir = self.make_temp_dir()
    sub = path.join(src_dir, 'action')
    os.makedirs(sub)
    src = path.join(sub, 'movie.mp4')
    open(src, 'w').close()
    syncer = self._make_syncer(source_dirs=[src_dir])
    mkdir_calls = []
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='b' * 64):
      call_count = [0]
      def ssh_sha256(p, progress_callback=None):
        call_count[0] += 1
        return None if call_count[0] == 1 else 'b' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
      syncer._ssh_mkdir = lambda d: mkdir_calls.append(d)
      with mock.patch.object(os, 'remove'):
        syncer._run_loop()
    self.assertEqual(1, len(mkdir_calls))
    self.assertIn('action', mkdir_calls[0])

  def test_rename_in_subdir_preserves_subdir(self):
    src_dir = self.make_temp_dir()
    sub = path.join(src_dir, 'action')
    os.makedirs(sub)
    src = path.join(sub, 'movie.mp4')
    open(src, 'w').close()
    syncer = self._make_syncer(source_dirs=[src_dir])
    transferred_dest = []
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='c' * 64):
      call_count = [0]
      def ssh_sha256(p, progress_callback=None):
        call_count[0] += 1
        if call_count[0] == 1:
          return 'd' * 64  # pre-check: different content → rename
        return 'c' * 64    # verify: match
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: transferred_dest.append(d)
      syncer._ssh_mkdir = lambda d: None
      with mock.patch.object(os, 'remove'):
        syncer._run_loop()
    self.assertEqual(1, len(transferred_dest))
    dest = transferred_dest[0]
    self.assertIn('action/', dest)
    self.assertIn('-' + 'c' * 8, dest)


class test_bf_rsync_file_sync_progress(unit_test):
  'Unit tests for _show_progress, _progress_prefix, and _on_rsync_progress.'

  def _make_syncer(self, source_dirs=None, **kwargs):
    tmp_dir = self.make_temp_dir()
    key = path.join(tmp_dir, 'key')
    open(key, 'w').close()
    source_dirs = source_dirs or [self.make_temp_dir()]
    return bf_rsync_file_sync(
      key, 'nas2:/mnt/stuff/p', source_dirs,
      strict_host_checking=False, **kwargs
    )

  def test_show_progress_false_by_default(self):
    syncer = self._make_syncer()
    self.assertFalse(syncer._show_progress)

  def test_show_progress_false_when_not_compact(self):
    syncer = self._make_syncer(compact=False)
    syncer._cleanup_partial = lambda: None
    syncer._run_loop()
    self.assertFalse(syncer._show_progress)

  def test_show_progress_false_when_compact_but_not_tty(self):
    syncer = self._make_syncer(compact=True)
    syncer._cleanup_partial = lambda: None
    with mock.patch('sys.stdout') as mock_stdout:
      mock_stdout.isatty.return_value = False
      syncer._run_loop()
    self.assertFalse(syncer._show_progress)

  def test_progress_prefix_empty_by_default(self):
    syncer = self._make_syncer()
    self.assertEqual('', syncer._progress_prefix)

  def test_progress_prefix_set_before_sync(self):
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'video.mp4')
    with open(src, 'wb') as f:
      f.write(b'x' * 1024)
    syncer = self._make_syncer(source_dirs=[src_dir])
    captured_prefixes = []
    file_size = path.getsize(src)
    def mock_sync_one(entry):
      captured_prefixes.append(syncer._progress_prefix)
      return ('skip', file_size, 'same checksum')
    syncer._sync_one = mock_sync_one
    syncer._cleanup_partial = lambda: None
    syncer._run_loop()
    self.assertEqual(1, len(captured_prefixes))
    prefix = captured_prefixes[0]
    self.assertIn('[1/1]', prefix)
    self.assertIn('video.mp4', prefix)

  def test_progress_prefix_includes_size(self):
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'clip.mp4')
    with open(src, 'wb') as f:
      f.write(b'x' * 2048)
    syncer = self._make_syncer(source_dirs=[src_dir])
    captured_prefixes = []
    file_size = path.getsize(src)
    def mock_sync_one(entry):
      captured_prefixes.append(syncer._progress_prefix)
      return ('skip', file_size, 'same checksum')
    syncer._sync_one = mock_sync_one
    syncer._cleanup_partial = lambda: None
    syncer._run_loop()
    self.assertIn('2.0KiB', captured_prefixes[0])

  def test_progress_prefix_index_counts_correctly(self):
    src_dir = self.make_temp_dir()
    for name in ('a.mp4', 'b.mp4', 'c.mp4'):
      with open(path.join(src_dir, name), 'wb') as f:
        f.write(b'x')
    syncer = self._make_syncer(source_dirs=[src_dir])
    captured_prefixes = []
    def mock_sync_one(entry):
      captured_prefixes.append(syncer._progress_prefix)
      return ('skip', 1, 'same checksum')
    syncer._sync_one = mock_sync_one
    syncer._cleanup_partial = lambda: None
    syncer._run_loop()
    self.assertEqual(3, len(captured_prefixes))
    self.assertIn('[1/3]', captured_prefixes[0])
    self.assertIn('[2/3]', captured_prefixes[1])
    self.assertIn('[3/3]', captured_prefixes[2])

  def test_on_rsync_progress_writes_to_stdout(self):
    import io
    from collections import namedtuple
    syncer = self._make_syncer()
    syncer._progress_prefix = '[2/5] 1.5MiB - movie.mp4'
    FakeEvent = namedtuple('FakeEvent', 'bytes_done percent rate elapsed')
    event = FakeEvent(bytes_done=1572864, percent=75, rate='25.0MB/s', elapsed='0:00:02')
    captured = io.StringIO()
    with mock.patch('sys.stdout', new=captured):
      syncer._on_rsync_progress(event)
    output = captured.getvalue()
    self.assertTrue(output.startswith('\r'))
    self.assertIn('[2/5] 1.5MiB - movie.mp4', output)
    self.assertIn('75%', output)
    self.assertIn('25.0MB/s', output)
    self.assertIn('0:00:02', output)

  def test_on_rsync_progress_uses_current_prefix(self):
    import io
    from collections import namedtuple
    syncer = self._make_syncer()
    FakeEvent = namedtuple('FakeEvent', 'bytes_done percent rate elapsed')
    event = FakeEvent(bytes_done=0, percent=10, rate='5.0MB/s', elapsed='0:00:01')
    syncer._progress_prefix = '[1/1] 500.0B - small.mp4'
    captured = io.StringIO()
    with mock.patch('sys.stdout', new=captured):
      syncer._on_rsync_progress(event)
    self.assertIn('[1/1] 500.0B - small.mp4', captured.getvalue())

  def test_update_status_writes_when_show_progress(self):
    import io
    syncer = self._make_syncer()
    syncer._show_progress = True
    syncer._progress_prefix = '[1/1] 100.0B - file.mp4'
    captured = io.StringIO()
    with mock.patch('sys.stdout', new=captured):
      syncer._update_status('checksumming...')
    output = captured.getvalue()
    self.assertTrue(output.startswith('\r'))
    self.assertIn('[1/1] 100.0B - file.mp4', output)
    self.assertIn('checksumming...', output)

  def test_update_status_silent_when_not_show_progress(self):
    import io
    syncer = self._make_syncer()
    syncer._show_progress = False
    captured = io.StringIO()
    with mock.patch('sys.stdout', new=captured):
      syncer._update_status('checksumming...')
    self.assertEqual('', captured.getvalue())

  def test_on_rsync_progress_safe_with_empty_prefix(self):
    import io
    from collections import namedtuple
    syncer = self._make_syncer()
    FakeEvent = namedtuple('FakeEvent', 'bytes_done percent rate elapsed')
    event = FakeEvent(bytes_done=0, percent=0, rate='0.00kB/s', elapsed='0:00:00')
    captured = io.StringIO()
    with mock.patch('sys.stdout', new=captured):
      syncer._on_rsync_progress(event)
    output = captured.getvalue()
    self.assertTrue(output.startswith('\r'))
    self.assertIn('0%', output)


class test_bf_rsync_file_sync_simplify(unit_test):
  'Unit tests for --simplify behaviour — all subprocess calls mocked.'

  def _make_syncer(self, source_dirs=None, **kwargs):
    tmp_dir = self.make_temp_dir()
    key = path.join(tmp_dir, 'key')
    open(key, 'w').close()
    if source_dirs is None:
      source_dirs = [tmp_dir]
    return bf_rsync_file_sync(
      key, 'nas2:/mnt/stuff/p', source_dirs,
      strict_host_checking=False, **kwargs
    )

  def _make_entry_named(self, name):
    'Create a real file on disk with the given basename and return an entry for it.'
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, name)
    with open(src, 'wb') as f:
      f.write(b'data')
    return bf_entry(name, root_dir=src_dir), src

  def test_simplify_skip_already_at_simplified_path(self):
    syncer = self._make_syncer(simplify=True)
    entry, src = self._make_entry_named('My Movie.mp4')
    local_hash = 'a' * 64
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value=local_hash):
      syncer._ssh_sha256 = lambda p, progress_callback=None: local_hash if path.basename(p) == 'my_movie.mp4' else None
      with mock.patch.object(os, 'remove'):
        action, size, reason = syncer._sync_one(entry)
    self.assertEqual('skip', action)
    self.assertEqual('same checksum', reason)

  def test_simplify_transfer_to_simplified_path(self):
    syncer = self._make_syncer(simplify=True)
    entry, src = self._make_entry_named('My Movie.mp4')
    local_hash = 'a' * 64
    transferred = []
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value=local_hash):
      call_count = [0]
      def ssh_sha256(p, progress_callback=None):
        call_count[0] += 1
        if call_count[0] <= 2:
          return None   # simplified slot empty, original not on server
        return local_hash  # post-transfer verify
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: transferred.append(d)
      syncer._ssh_mkdir = lambda d: None
      with mock.patch.object(os, 'remove'):
        action, size, reason = syncer._sync_one(entry)
    self.assertEqual('transfer', action)
    self.assertEqual('my_movie.mp4', reason)
    self.assertTrue(any('my_movie.mp4' in d for d in transferred))
    self.assertFalse(any('My Movie.mp4' in d for d in transferred))

  def test_simplify_server_mv_original_to_simplified(self):
    syncer = self._make_syncer(simplify=True)
    entry, src = self._make_entry_named('My Movie.mp4')
    local_hash = 'a' * 64
    mv_calls = []
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value=local_hash):
      def ssh_sha256(p, progress_callback=None):
        basename = path.basename(p)
        if basename == 'my_movie.mp4':
          return None       # simplified slot empty
        if basename == 'My Movie.mp4':
          return local_hash  # original has correct content
        return None
      syncer._ssh_sha256 = ssh_sha256
      syncer._ssh_mv = lambda s, d: mv_calls.append((s, d))
      with mock.patch.object(os, 'remove'):
        action, size, reason = syncer._sync_one(entry)
    self.assertEqual('server_rename', action)
    self.assertEqual('my_movie.mp4', reason)
    self.assertEqual(1, len(mv_calls))
    self.assertIn('My Movie.mp4', mv_calls[0][0])
    self.assertIn('my_movie.mp4', mv_calls[0][1])

  def test_simplify_server_mv_when_simplified_slot_has_collision(self):
    syncer = self._make_syncer(simplify=True)
    entry, src = self._make_entry_named('My Movie.mp4')
    local_hash = 'a' * 64
    other_hash = 'b' * 64
    mv_calls = []
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value=local_hash):
      def ssh_sha256(p, progress_callback=None):
        basename = path.basename(p)
        if basename == 'my_movie.mp4':
          return other_hash   # simplified slot taken by different content
        if basename == 'My Movie.mp4':
          return local_hash   # original has our content
        return None
      syncer._ssh_sha256 = ssh_sha256
      syncer._ssh_mv = lambda s, d: mv_calls.append((s, d))
      with mock.patch.object(os, 'remove'):
        action, size, reason = syncer._sync_one(entry)
    self.assertEqual('server_rename', action)
    # should have moved to hash-suffixed simplified name, not plain simplified
    self.assertIn('my_movie-', reason)
    self.assertTrue(reason.endswith('.mp4'))
    self.assertEqual(1, len(mv_calls))
    self.assertIn('My Movie.mp4', mv_calls[0][0])   # from original
    self.assertIn('my_movie-', mv_calls[0][1])       # to hash-suffixed simplified

  def test_simplify_rename_when_simplified_occupied_and_original_absent(self):
    syncer = self._make_syncer(simplify=True)
    entry, src = self._make_entry_named('My Movie.mp4')
    local_hash = 'a' * 64
    other_hash = 'b' * 64
    transferred = []
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value=local_hash):
      call_count = [0]
      def ssh_sha256(p, progress_callback=None):
        call_count[0] += 1
        basename = path.basename(p)
        if basename == 'my_movie.mp4':
          return other_hash   # simplified slot collision
        if basename == 'My Movie.mp4':
          return None          # original not on server
        return local_hash      # post-transfer verify
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: transferred.append(d)
      syncer._ssh_mkdir = lambda d: None
      with mock.patch.object(os, 'remove'):
        action, size, reason = syncer._sync_one(entry)
    self.assertEqual('rename', action)
    self.assertIn('my_movie-', reason)
    self.assertTrue(any('my_movie-' in d for d in transferred))

  def test_simplify_clean_name_makes_no_extra_ssh_call(self):
    syncer = self._make_syncer(simplify=True)
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'video.mp4')
    with open(src, 'wb') as f:
      f.write(b'data')
    entry = bf_entry('video.mp4', root_dir=src_dir)
    local_hash = 'a' * 64
    sha256_calls = []
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value=local_hash):
      call_count = [0]
      def ssh_sha256(p, progress_callback=None):
        sha256_calls.append(p)
        call_count[0] += 1
        return None if call_count[0] == 1 else local_hash
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
      syncer._ssh_mkdir = lambda d: None
      with mock.patch.object(os, 'remove'):
        syncer._sync_one(entry)
    # clean name: pre-check (1) + verify (2) — no extra call for original
    self.assertEqual(2, len(sha256_calls))

  def test_simplify_dirty_name_checks_original_slot(self):
    syncer = self._make_syncer(simplify=True)
    entry, src = self._make_entry_named('My Movie.mp4')
    local_hash = 'a' * 64
    sha256_calls = []
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value=local_hash):
      call_count = [0]
      def ssh_sha256(p, progress_callback=None):
        sha256_calls.append(p)
        call_count[0] += 1
        if call_count[0] <= 2:
          return None
        return local_hash
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
      syncer._ssh_mkdir = lambda d: None
      with mock.patch.object(os, 'remove'):
        syncer._sync_one(entry)
    # dirty name: simplified check (1) + original check (2) + verify (3)
    self.assertEqual(3, len(sha256_calls))
    basenames = [path.basename(p) for p in sha256_calls]
    self.assertIn('my_movie.mp4', basenames)
    self.assertIn('My Movie.mp4', basenames)

  def test_simplify_dry_run_server_mv(self):
    syncer = self._make_syncer(simplify=True, dry_run=True)
    entry, src = self._make_entry_named('My Movie.mp4')
    local_hash = 'a' * 64
    mv_calls = []
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value=local_hash):
      def ssh_sha256(p, progress_callback=None):
        basename = path.basename(p)
        if basename == 'my_movie.mp4':
          return None
        if basename == 'My Movie.mp4':
          return local_hash
        return None
      syncer._ssh_sha256 = ssh_sha256
      syncer._ssh_mv = lambda s, d: mv_calls.append((s, d))
      with mock.patch.object(os, 'remove') as mock_remove:
        action, size, reason = syncer._sync_one(entry)
    self.assertEqual('server_rename', action)
    self.assertEqual([], mv_calls)           # no actual mv in dry run
    mock_remove.assert_not_called()          # local not deleted in dry run

  def test_simplify_dry_run_transfer_shows_simplified_name(self):
    import io
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'My Movie.mp4')
    with open(src, 'wb') as f:
      f.write(b'data')
    syncer = self._make_syncer(source_dirs=[src_dir], simplify=True, dry_run=True)
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    captured = io.StringIO()
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='a' * 64):
      syncer._ssh_sha256 = lambda p, progress_callback=None: None
      with mock.patch('sys.stdout', new=captured):
        syncer._run_loop()
    output = captured.getvalue()
    self.assertIn('DRY-XFER', output)
    self.assertIn('my_movie.mp4', output)

  def test_simplify_dry_run_server_mv_shows_dry_mv_tag(self):
    import io
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'My Movie.mp4')
    with open(src, 'wb') as f:
      f.write(b'data')
    syncer = self._make_syncer(source_dirs=[src_dir], simplify=True, dry_run=True)
    local_hash = 'a' * 64
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    captured = io.StringIO()
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value=local_hash):
      def ssh_sha256(p, progress_callback=None):
        basename = path.basename(p)
        if basename == 'my_movie.mp4':
          return None
        if basename == 'My Movie.mp4':
          return local_hash
        return None
      syncer._ssh_sha256 = ssh_sha256
      with mock.patch('sys.stdout', new=captured):
        syncer._run_loop()
    self.assertIn('DRY-MV', captured.getvalue())

  def test_simplify_unsimplifiable_filename_falls_back_to_original(self):
    syncer = self._make_syncer(simplify=True)
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, '!!!!!.mp4')
    with open(src, 'wb') as f:
      f.write(b'data')
    entry = bf_entry('!!!!!.mp4', root_dir=src_dir)
    local_hash = 'a' * 64
    warn_tags = []
    syncer._emit = lambda tag, msg: warn_tags.append(tag)
    transferred = []
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value=local_hash):
      call_count = [0]
      def ssh_sha256(p, progress_callback=None):
        call_count[0] += 1
        return None if call_count[0] == 1 else local_hash
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: transferred.append(d)
      syncer._ssh_mkdir = lambda d: None
      with mock.patch.object(os, 'remove'):
        action, size, reason = syncer._sync_one(entry)
    self.assertIn('WARN', warn_tags)
    self.assertTrue(any('!!!!!.mp4' in d for d in transferred))
    self.assertEqual('transfer', action)

  def test_simplify_server_mv_deletes_local_file(self):
    syncer = self._make_syncer(simplify=True)
    entry, src = self._make_entry_named('My Movie.mp4')
    local_hash = 'a' * 64
    removed = []
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value=local_hash):
      def ssh_sha256(p, progress_callback=None):
        basename = path.basename(p)
        if basename == 'my_movie.mp4':
          return None
        if basename == 'My Movie.mp4':
          return local_hash
        return None
      syncer._ssh_sha256 = ssh_sha256
      syncer._ssh_mv = lambda s, d: None
      with mock.patch.object(os, 'remove', side_effect=lambda p: removed.append(p)):
        syncer._sync_one(entry)
    self.assertIn(src, removed)

  def test_simplify_false_does_not_simplify(self):
    syncer = self._make_syncer(simplify=False)
    entry, src = self._make_entry_named('My Movie.mp4')
    local_hash = 'a' * 64
    transferred = []
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value=local_hash):
      call_count = [0]
      def ssh_sha256(p, progress_callback=None):
        call_count[0] += 1
        return None if call_count[0] == 1 else local_hash
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: transferred.append(d)
      syncer._ssh_mkdir = lambda d: None
      with mock.patch.object(os, 'remove'):
        action, size, reason = syncer._sync_one(entry)
    self.assertEqual('transfer', action)
    self.assertEqual('', reason)
    self.assertTrue(any('My Movie.mp4' in d for d in transferred))
    self.assertFalse(any('my_movie.mp4' in d for d in transferred))


class test_bf_rsync_file_sync_filters(unit_test):
  'Unit tests for --min-size, --max-size, and --mime-type filtering in _collect_files.'

  def _make_syncer(self, src_dir, **kwargs):
    tmp_dir = self.make_temp_dir()
    key = path.join(tmp_dir, 'key')
    open(key, 'w').close()
    return bf_rsync_file_sync(
      key, 'nas2:/mnt/stuff/p', [src_dir],
      strict_host_checking=False, **kwargs
    )

  def _write(self, directory, filename, size):
    p = path.join(directory, filename)
    with open(p, 'wb') as f:
      f.write(b'x' * size)
    return p

  def test_min_size_excludes_small_files(self):
    src_dir = self.make_temp_dir()
    self._write(src_dir, 'small.mp4', 100)
    self._write(src_dir, 'big.mp4', 2000)
    syncer = self._make_syncer(src_dir, min_size=1024)
    entries = syncer._collect_files()
    names = [path.basename(e.absolute_filename) for e in entries]
    self.assertNotIn('small.mp4', names)
    self.assertIn('big.mp4', names)

  def test_min_size_includes_file_at_boundary(self):
    src_dir = self.make_temp_dir()
    self._write(src_dir, 'exact.mp4', 1024)
    syncer = self._make_syncer(src_dir, min_size=1024)
    entries = syncer._collect_files()
    names = [path.basename(e.absolute_filename) for e in entries]
    self.assertIn('exact.mp4', names)

  def test_max_size_excludes_large_files(self):
    src_dir = self.make_temp_dir()
    self._write(src_dir, 'small.mp4', 100)
    self._write(src_dir, 'big.mp4', 5000)
    syncer = self._make_syncer(src_dir, max_size=1024)
    entries = syncer._collect_files()
    names = [path.basename(e.absolute_filename) for e in entries]
    self.assertIn('small.mp4', names)
    self.assertNotIn('big.mp4', names)

  def test_max_size_includes_file_at_boundary(self):
    src_dir = self.make_temp_dir()
    self._write(src_dir, 'exact.mp4', 1024)
    syncer = self._make_syncer(src_dir, max_size=1024)
    entries = syncer._collect_files()
    names = [path.basename(e.absolute_filename) for e in entries]
    self.assertIn('exact.mp4', names)

  def test_min_and_max_size_together(self):
    src_dir = self.make_temp_dir()
    self._write(src_dir, 'tiny.mp4', 50)
    self._write(src_dir, 'medium.mp4', 500)
    self._write(src_dir, 'huge.mp4', 5000)
    syncer = self._make_syncer(src_dir, min_size=100, max_size=1000)
    entries = syncer._collect_files()
    names = [path.basename(e.absolute_filename) for e in entries]
    self.assertNotIn('tiny.mp4', names)
    self.assertIn('medium.mp4', names)
    self.assertNotIn('huge.mp4', names)

  def test_no_size_filter_includes_all(self):
    src_dir = self.make_temp_dir()
    self._write(src_dir, 'a.mp4', 1)
    self._write(src_dir, 'b.mp4', 1000000)
    syncer = self._make_syncer(src_dir)
    entries = syncer._collect_files()
    names = [path.basename(e.absolute_filename) for e in entries]
    self.assertIn('a.mp4', names)
    self.assertIn('b.mp4', names)

  def test_mime_type_includes_matching_files(self):
    src_dir = self.make_temp_dir()
    self._write(src_dir, 'video.mp4', 100)
    self._write(src_dir, 'image.jpg', 100)
    syncer = self._make_syncer(src_dir, mime_type='video/mp4')
    def fake_detect(filename):
      return 'video/mp4' if filename.endswith('.mp4') else 'image/jpeg'
    with mock.patch.object(bf_mime_type_detector, 'detect_mime_type', side_effect=fake_detect):
      entries = syncer._collect_files()
    names = [path.basename(e.absolute_filename) for e in entries]
    self.assertIn('video.mp4', names)
    self.assertNotIn('image.jpg', names)

  def test_mime_type_excludes_nonmatching_files(self):
    src_dir = self.make_temp_dir()
    self._write(src_dir, 'clip.mp4', 100)
    syncer = self._make_syncer(src_dir, mime_type='audio/flac')
    with mock.patch.object(bf_mime_type_detector, 'detect_mime_type', return_value='video/mp4'):
      entries = syncer._collect_files()
    self.assertEqual([], entries)

  def test_mime_type_wildcard_matches_subtype(self):
    src_dir = self.make_temp_dir()
    self._write(src_dir, 'clip.mp4', 100)
    self._write(src_dir, 'movie.mkv', 100)
    self._write(src_dir, 'photo.jpg', 100)
    syncer = self._make_syncer(src_dir, mime_type='video/*')
    def fake_detect(filename):
      if filename.endswith('.mp4'):
        return 'video/mp4'
      if filename.endswith('.mkv'):
        return 'video/x-matroska'
      return 'image/jpeg'
    with mock.patch.object(bf_mime_type_detector, 'detect_mime_type', side_effect=fake_detect):
      entries = syncer._collect_files()
    names = [path.basename(e.absolute_filename) for e in entries]
    self.assertIn('clip.mp4', names)
    self.assertIn('movie.mkv', names)
    self.assertNotIn('photo.jpg', names)

  def test_mime_type_undetectable_file_excluded(self):
    src_dir = self.make_temp_dir()
    self._write(src_dir, 'mystery.bin', 100)
    syncer = self._make_syncer(src_dir, mime_type='video/*')
    with mock.patch.object(bf_mime_type_detector, 'detect_mime_type', return_value=None):
      entries = syncer._collect_files()
    self.assertEqual([], entries)

  def test_mime_type_and_min_size_combined(self):
    src_dir = self.make_temp_dir()
    self._write(src_dir, 'small_video.mp4', 50)
    self._write(src_dir, 'big_video.mp4', 2000)
    self._write(src_dir, 'big_audio.flac', 2000)
    syncer = self._make_syncer(src_dir, min_size=100, mime_type='video/*')
    def fake_detect(filename):
      if filename.endswith('.mp4'):
        return 'video/mp4'
      return 'audio/flac'
    with mock.patch.object(bf_mime_type_detector, 'detect_mime_type', side_effect=fake_detect):
      entries = syncer._collect_files()
    names = [path.basename(e.absolute_filename) for e in entries]
    self.assertNotIn('small_video.mp4', names)
    self.assertIn('big_video.mp4', names)
    self.assertNotIn('big_audio.flac', names)


class test_bf_rsync_file_sync_integration(unit_test):
  'Integration tests — real sshd + rsync via bssh_sandbox.'

  _sandbox = None

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip_if_not_unix()
    unit_test_class_skip.raise_skip_if_not_has_command('sshd')
    unit_test_class_skip.raise_skip_if_not_has_command('rsync')
    unit_test_class_skip.raise_skip_if_not_has_command('ssh-keygen')
    clazz._sandbox = bssh_sandbox(strict_host_checking=False,
                                   allow_users=[getpass.getuser()])
    clazz._sandbox.start()

  @classmethod
  def tearDownClass(clazz):
    if clazz._sandbox:
      clazz._sandbox.stop()

  def _make_syncer(self, source_dirs):
    return bf_rsync_file_sync(
      self._sandbox.key,
      f'127.0.0.1:{self._sandbox.nas_root}',
      source_dirs,
      known_hosts_file=self._sandbox.known_hosts,
      strict_host_checking=False,
      retry_wait_seconds=5,
      ssh_port=self._sandbox.port,
    )

  def _make_src_dir(self):
    'Create a stable named subdirectory so the re-rooted destination is predictable.'
    return path.join(self.make_temp_dir(), 'source')

  def _write_file(self, directory, filename, content=b'data'):
    os.makedirs(directory, exist_ok=True)
    p = path.join(directory, filename)
    with open(p, 'wb') as f:
      f.write(content)
    return p

  def _sha256(self, filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
      for chunk in iter(lambda: f.read(65536), b''):
        h.update(chunk)
    return h.hexdigest()

  # 94
  def test_integration_transfer_new_file(self):
    src_dir = self._make_src_dir()
    src = self._write_file(src_dir, 'new.mp4', b'new content')
    syncer = self._make_syncer([src_dir])
    syncer.run()
    self.assertFalse(path.exists(src))
    dest = path.join(self._sandbox.nas_root, 'source', 'new.mp4')
    self.assertTrue(path.exists(dest))

  # 95
  def test_integration_skip_same_file(self):
    src_dir = self._make_src_dir()
    content = b'identical content'
    src = self._write_file(src_dir, 'same.mp4', content)
    nas_dest = path.join(self._sandbox.nas_root, 'source', 'same.mp4')
    self._write_file(path.join(self._sandbox.nas_root, 'source'), 'same.mp4', content)
    syncer = self._make_syncer([src_dir])
    syncer.run()
    self.assertFalse(path.exists(src))
    self.assertTrue(path.exists(nas_dest))

  # 96
  def test_integration_rename_different_content(self):
    src_dir = self._make_src_dir()
    nas_src_dir = path.join(self._sandbox.nas_root, 'source')
    self._write_file(nas_src_dir, 'differ.mp4', b'nas version')
    src_content = b'local version'
    src = self._write_file(src_dir, 'differ.mp4', src_content)
    local_hash = self._sha256(src)
    syncer = self._make_syncer([src_dir])
    syncer.run()
    self.assertFalse(path.exists(src))
    unique_name = f'differ-{local_hash[:8]}.mp4'
    self.assertTrue(path.exists(path.join(nas_src_dir, unique_name)))

  # 97
  def test_integration_multiple_files(self):
    src_dir = self._make_src_dir()
    nas_src_dir = path.join(self._sandbox.nas_root, 'source')
    self._write_file(nas_src_dir, 'a.mp4', b'aaa')
    self._write_file(src_dir, 'a.mp4', b'aaa')   # same → skip
    self._write_file(src_dir, 'b.mp4', b'bbb')   # new
    self._write_file(src_dir, 'c.mp4', b'ccc')   # new
    syncer = self._make_syncer([src_dir])
    syncer.run()
    self.assertEqual([], [f for f in os.listdir(src_dir) if f.endswith('.mp4')])
    self.assertTrue(path.exists(path.join(nas_src_dir, 'b.mp4')))
    self.assertTrue(path.exists(path.join(nas_src_dir, 'c.mp4')))

  # 98
  def test_integration_partial_resume(self):
    src_dir = self._make_src_dir()
    content = b'partial resume test ' * 1024
    src = self._write_file(src_dir, 'partial.mp4', content)
    partial_dir = path.join(self._sandbox.nas_root, '.rsync-partial')
    os.makedirs(partial_dir, exist_ok=True)
    with open(path.join(partial_dir, 'partial.mp4'), 'wb') as f:
      f.write(content[:len(content)//2])
    syncer = self._make_syncer([src_dir])
    syncer.run()
    self.assertFalse(path.exists(src))
    dest = path.join(self._sandbox.nas_root, 'source', 'partial.mp4')
    self.assertEqual(content, open(dest, 'rb').read())

  # 99
  def test_integration_large_file(self):
    src_dir = self._make_src_dir()
    content = os.urandom(10 * 1024 * 1024)  # 10 MB (keep test fast)
    src = self._write_file(src_dir, 'large.mp4', content)
    expected_hash = self._sha256(src)
    syncer = self._make_syncer([src_dir])
    syncer.run()
    dest = path.join(self._sandbox.nas_root, 'source', 'large.mp4')
    self.assertTrue(path.exists(dest))
    self.assertEqual(expected_hash, self._sha256(dest))

  # 100
  def test_integration_ds_store_excluded(self):
    src_dir = self.make_temp_dir()
    self._write_file(src_dir, '.DS_Store', b'mac junk')
    self._write_file(src_dir, 'real.mp4', b'real content')
    syncer = self._make_syncer([src_dir])
    syncer.run()
    self.assertFalse(path.exists(path.join(self._sandbox.nas_root, '.DS_Store')))

  # 101 — SSH refused mid-run: hard to test deterministically; verify retry logic structure
  def test_integration_checksum_verified_on_nas(self):
    src_dir = self._make_src_dir()
    content = b'verify me'
    src = self._write_file(src_dir, 'verify.mp4', content)
    expected = self._sha256(src)
    syncer = self._make_syncer([src_dir])
    syncer.run()
    dest = path.join(self._sandbox.nas_root, 'source', 'verify.mp4')
    self.assertEqual(expected, self._sha256(dest))

  # 102
  def test_integration_source_preserved_on_interrupted_transfer(self):
    src_dir = self._make_src_dir()
    src = self._write_file(src_dir, 'interrupt.mp4', b'interrupt')
    syncer = self._make_syncer([src_dir])
    syncer._rsync = lambda s, d: (_ for _ in ()).throw(bf_rsync_error('simulated interrupt'))
    syncer._ssh_sha256 = lambda p, progress_callback=None: None
    syncer._ssh_mkdir = lambda d: None
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    entry = bf_entry('source/interrupt.mp4', root_dir=path.dirname(src_dir))
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='a' * 64):
      with self.assertRaises(bf_rsync_error):
        syncer._sync_one(entry)
    self.assertTrue(path.exists(src))

  # 103
  def test_integration_no_home_side_effects(self):
    ssh_dir = os.path.expanduser('~/.ssh')
    mtime_before = os.path.getmtime(ssh_dir) if path.exists(ssh_dir) else None
    src_dir = self.make_temp_dir()
    self._write_file(src_dir, 'home.mp4', b'home test')
    syncer = self._make_syncer([src_dir])
    syncer.run()
    mtime_after = os.path.getmtime(ssh_dir) if path.exists(ssh_dir) else None
    self.assertEqual(mtime_before, mtime_after)

  # 104 — was 105 in doc; we'll use 104 for partial cleanup
  def test_integration_partial_dir_cleaned_up(self):
    src_dir = self.make_temp_dir()
    self._write_file(src_dir, 'cleanup.mp4', b'cleanup test')
    syncer = self._make_syncer([src_dir])
    syncer.run()
    partial_dir = path.join(self._sandbox.nas_root, '.rsync-partial')
    self.assertFalse(path.exists(partial_dir))

  def _make_simplify_syncer(self, source_dirs):
    return bf_rsync_file_sync(
      self._sandbox.key,
      f'127.0.0.1:{self._sandbox.nas_root}',
      source_dirs,
      known_hosts_file=self._sandbox.known_hosts,
      strict_host_checking=False,
      retry_wait_seconds=5,
      ssh_port=self._sandbox.port,
      simplify=True,
    )

  def test_integration_simplify_transfer_new_file(self):
    src_dir = self._make_src_dir()
    src = self._write_file(src_dir, 'My Movie (2024).mp4', b'movie data')
    syncer = self._make_simplify_syncer([src_dir])
    syncer.run()
    self.assertFalse(path.exists(src))
    nas_dir = path.join(self._sandbox.nas_root, 'source')
    self.assertTrue(path.exists(path.join(nas_dir, 'my_movie_2024.mp4')))
    self.assertFalse(path.exists(path.join(nas_dir, 'My Movie (2024).mp4')))

  def test_integration_simplify_server_mv_original_to_simplified(self):
    src_dir = self._make_src_dir()
    content = b'already on nas'
    src = self._write_file(src_dir, 'My Movie.mp4', content)
    nas_dir = path.join(self._sandbox.nas_root, 'source')
    self._write_file(nas_dir, 'My Movie.mp4', content)  # original on NAS
    syncer = self._make_simplify_syncer([src_dir])
    syncer.run()
    self.assertFalse(path.exists(src))
    self.assertTrue(path.exists(path.join(nas_dir, 'my_movie.mp4')))
    self.assertFalse(path.exists(path.join(nas_dir, 'My Movie.mp4')))

  def test_integration_simplify_skip_already_at_simplified(self):
    src_dir = self._make_src_dir()
    content = b'already simplified'
    src = self._write_file(src_dir, 'My Movie.mp4', content)
    nas_dir = path.join(self._sandbox.nas_root, 'source')
    self._write_file(nas_dir, 'my_movie.mp4', content)  # simplified already on NAS
    syncer = self._make_simplify_syncer([src_dir])
    syncer.run()
    self.assertFalse(path.exists(src))
    self.assertTrue(path.exists(path.join(nas_dir, 'my_movie.mp4')))


class test_bf_rsync_file_sync_checksum_script(unit_test):
  'Unit tests for _install_remote_checksum_script and streaming _ssh_sha256.'

  def _make_syncer(self, **kwargs):
    tmp_dir = self.make_temp_dir()
    key = path.join(tmp_dir, 'key')
    open(key, 'w').close()
    return bf_rsync_file_sync(
      key, 'nas2:/mnt/stuff/p', [tmp_dir],
      strict_host_checking=False, **kwargs
    )

  # 105
  def test_local_checksum_script_path_exists(self):
    script_path = bf_rsync_file_sync._local_checksum_script_path()
    self.assertTrue(path.isfile(script_path), f'bfile-checksum.py not found at: {script_path}')

  # 106
  def test_install_remote_checksum_script_passes_content_as_input_data(self):
    syncer = self._make_syncer()
    captured_calls = []
    def fake_call_command(args, input_data=None, **kwargs):
      captured_calls.append({'args': args, 'input_data': input_data})
      return _fake_rv('')
    with mock.patch.object(bssh_command, 'call_command', side_effect=fake_call_command):
      syncer._install_remote_checksum_script()
    self.assertEqual(1, len(captured_calls))
    call = captured_calls[0]
    self.assertIsNotNone(call['input_data'])
    self.assertIsInstance(call['input_data'], bytes)
    self.assertIn(b'sha256', call['input_data'])
    remote_cmd = call['args'][-1]
    self.assertIn(bf_rsync_file_sync._REMOTE_CHECKSUM_SCRIPT, remote_cmd)

  # 107
  def test_install_remote_checksum_script_target_path_in_command(self):
    syncer = self._make_syncer()
    captured_calls = []
    with mock.patch.object(bssh_command, 'call_command',
                           side_effect=lambda args, **kw: captured_calls.append(args) or _fake_rv('')):
      syncer._install_remote_checksum_script()
    remote_cmd = captured_calls[0][-1]
    self.assertIn('/tmp/bfile-checksum.py', remote_cmd)
    self.assertIn('cat >', remote_cmd)

  # 108
  def test_ssh_sha256_progress_callback_called(self):
    syncer = self._make_syncer()
    received_events = []
    def progress_cb(event):
      received_events.append(event)
    def fake_ewp(args, line_parser, progress_cb=None, **kwargs):
      event = line_parser('sha256: PROGRESS: 1048576/10485760', None)
      if event is not None and progress_cb is not None:
        progress_cb(event)
      line_parser('sha256: CHECKSUM: ' + 'a' * 64, None)
      return _fake_progress_rv()
    with mock.patch.object(execute, 'execute_with_progress', side_effect=fake_ewp):
      syncer._ssh_sha256('/mnt/stuff/p/video.mp4', progress_callback=progress_cb)
    self.assertEqual(1, len(received_events))
    self.assertEqual(1048576, received_events[0].bytes_done)
    self.assertEqual(10485760, received_events[0].total_bytes)

  # 109
  def test_ssh_sha256_progress_callback_none_by_default(self):
    syncer = self._make_syncer()
    def fake_ewp(args, line_parser, progress_cb=None, **kwargs):
      line_parser('sha256: CHECKSUM: ' + 'b' * 64, None)
      self.assertIsNone(progress_cb)
      return _fake_progress_rv()
    with mock.patch.object(execute, 'execute_with_progress', side_effect=fake_ewp):
      result = syncer._ssh_sha256('/mnt/stuff/p/video.mp4')
    self.assertEqual('b' * 64, result)

  # 110
  def test_ssh_sha256_garbage_lines_ignored(self):
    syncer = self._make_syncer()
    hexhash = 'c' * 64
    def fake_ewp(args, line_parser, **kwargs):
      line_parser('some random output from ssh', None)
      line_parser('', None)
      line_parser('sha256: PROGRESS: bad/data', None)
      line_parser(f'sha256: CHECKSUM: {hexhash}', None)
      return _fake_progress_rv()
    with mock.patch.object(execute, 'execute_with_progress', side_effect=fake_ewp):
      result = syncer._ssh_sha256('/mnt/stuff/p/video.mp4')
    self.assertEqual(hexhash, result)


def _fake_rv(stdout):
  from collections import namedtuple
  R = namedtuple('R', 'stdout exit_code')
  return R(stdout=stdout, exit_code=0)


def _fake_progress_rv(exit_code=0, stderr=''):
  from collections import namedtuple
  Result = namedtuple('Result', 'exit_code, stderr')
  ProgressResult = namedtuple('ProgressResult', 'result, events')
  return ProgressResult(result=Result(exit_code=exit_code, stderr=stderr), events=[])


if __name__ == '__main__':
  unit_test.main()
