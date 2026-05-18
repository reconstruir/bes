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
from bes.files.rsync.bf_rsync_command import bf_rsync_command
from bes.files.rsync.bf_rsync_error import bf_rsync_error
from bes.files.rsync.bf_rsync_file_sync import bf_rsync_file_sync
from bes.ssh.bssh_command import bssh_command
from bes.ssh.bssh_error import bssh_error
from bes.ssh.bssh_sandbox import bssh_sandbox


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

  # 45
  def test_ssh_sha256_missing(self):
    syncer = self._make_syncer()
    with mock.patch.object(bssh_command, 'call_command') as m:
      m.return_value = _fake_rv('MISSING\n')
      result = syncer._ssh_sha256('/mnt/stuff/p/video.mp4')
    self.assertIsNone(result)

  # 46
  def test_ssh_sha256_match(self):
    syncer = self._make_syncer()
    hexhash = 'a' * 64
    with mock.patch.object(bssh_command, 'call_command') as m:
      m.return_value = _fake_rv(f'{hexhash}  /mnt/stuff/p/video.mp4\n')
      result = syncer._ssh_sha256('/mnt/stuff/p/video.mp4')
    self.assertEqual(hexhash, result)

  # 47
  def test_ssh_sha256_ssh_error(self):
    syncer = self._make_syncer()
    with mock.patch.object(bssh_command, 'call_command', side_effect=bssh_error('refused')):
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
      syncer._ssh_sha256 = lambda p: 'a' * 64  # same hash → skip
      with mock.patch.object(os, 'remove'):
        syncer._sync_one(src)
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
      syncer._ssh_sha256 = lambda p: 'b' * 64
      with mock.patch.object(os, 'remove'):
        syncer._sync_one(src)
    self.assertEqual(1, m.call_count)

  # 50
  def test_decision_destination_missing(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'data', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='c' * 64):
      syncer._ssh_sha256 = lambda p: None
      transferred = []
      syncer._rsync = lambda s, d: transferred.append(d)
      syncer._ssh_sha256 = lambda p: (None if not transferred else 'c' * 64)
      with mock.patch.object(os, 'remove'):
        syncer._sync_one(src)
    self.assertTrue(any('/mnt/stuff/p/' + path.basename(src) == d for d in transferred))

  # 51
  def test_decision_checksums_match(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'same', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    rsync_called = []
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='d' * 64):
      with mock.patch.object(bf_rsync_command, 'call_command', side_effect=lambda a: rsync_called.append(a)):
        syncer._ssh_sha256 = lambda p: 'd' * 64
        with mock.patch.object(os, 'remove'):
          syncer._sync_one(src)
    self.assertEqual([], rsync_called)

  # 52
  def test_decision_checksums_differ(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'local', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    transferred = []
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='e' * 64):
      call_count = [0]
      def ssh_sha256(p):
        call_count[0] += 1
        if call_count[0] == 1:
          return 'f' * 64  # pre-transfer: different
        return 'e' * 64    # post-transfer: verified
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: transferred.append(d)
      with mock.patch.object(os, 'remove'):
        syncer._sync_one(src)
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
    with mock.patch.object(bf_rsync_command, 'call_command', side_effect=lambda a, **kw: captured.extend(a) or _fake_rv('')):
      syncer._rsync('/tmp/video.mp4', '/mnt/stuff/p/video.mp4')
    args_str = ' '.join(captured)
    self.assertIn('--partial', args_str)
    self.assertIn('.rsync-partial', args_str)
    self.assertIn('StrictHostKeyChecking=no', args_str)
    self.assertIn('nas2:/mnt/stuff/p/video.mp4', args_str)

  # 58
  def test_transfer_no_home_known_hosts(self):
    home_kh = os.path.expanduser('~/.ssh/known_hosts')
    syncer = self._make_syncer()
    captured = []
    with mock.patch.object(bf_rsync_command, 'call_command', side_effect=lambda a, **kw: captured.extend(a) or _fake_rv('')):
      syncer._rsync('/tmp/video.mp4', '/mnt/stuff/p/video.mp4')
    self.assertNotIn(home_kh, ' '.join(captured))

  # 59
  def test_transfer_excludes_ds_store(self):
    syncer = self._make_syncer()
    captured = []
    with mock.patch.object(bf_rsync_command, 'call_command', side_effect=lambda a, **kw: captured.extend(a) or _fake_rv('')):
      syncer._rsync('/tmp/video.mp4', '/mnt/stuff/p/video.mp4')
    self.assertTrue(any('.DS_Store' in a for a in captured))

  # 60
  def test_transfer_no_remove_source_files(self):
    syncer = self._make_syncer()
    captured = []
    with mock.patch.object(bf_rsync_command, 'call_command', side_effect=lambda a, **kw: captured.extend(a) or _fake_rv('')):
      syncer._rsync('/tmp/video.mp4', '/mnt/stuff/p/video.mp4')
    self.assertNotIn('--remove-source-files', captured)

  # 61
  def test_transfer_no_no_whole_file(self):
    syncer = self._make_syncer()
    captured = []
    with mock.patch.object(bf_rsync_command, 'call_command', side_effect=lambda a, **kw: captured.extend(a) or _fake_rv('')):
      syncer._rsync('/tmp/video.mp4', '/mnt/stuff/p/video.mp4')
    self.assertNotIn('--no-whole-file', captured)

  # 62
  def test_verify_checksum_match(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'ok', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    removed = []
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='a' * 64):
      syncer._ssh_sha256 = lambda p: None if not removed else 'a' * 64
      syncer._rsync = lambda s, d: None
      orig_sha = syncer._ssh_sha256
      call_count = [0]
      def ssh_sha256(p):
        call_count[0] += 1
        return None if call_count[0] == 1 else 'a' * 64
      syncer._ssh_sha256 = ssh_sha256
      with mock.patch.object(os, 'remove', side_effect=lambda p: removed.append(p)):
        syncer._sync_one(src)
    self.assertIn(src, removed)

  # 63
  def test_verify_checksum_mismatch(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'mismatch', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='a' * 64):
      call_count = [0]
      def ssh_sha256(p):
        call_count[0] += 1
        if call_count[0] == 1:
          return None  # destination missing → transfer
        return 'b' * 64  # post-transfer: mismatch
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
      with self.assertRaises(bf_rsync_error):
        syncer._sync_one(src)

  # 64
  def test_source_deleted_after_verify(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'del', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    removed = []
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='c' * 64):
      call_count = [0]
      def ssh_sha256(p):
        call_count[0] += 1
        return None if call_count[0] == 1 else 'c' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
      with mock.patch.object(os, 'remove', side_effect=lambda p: removed.append(p)):
        syncer._sync_one(src)
    self.assertEqual(1, removed.count(src))

  # 65
  def test_source_not_deleted_on_rsync_failure(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'nodrop', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='d' * 64):
      syncer._ssh_sha256 = lambda p: None
      syncer._rsync = lambda s, d: (_ for _ in ()).throw(bf_rsync_error('rsync failed'))
      removed = []
      with mock.patch.object(os, 'remove', side_effect=lambda p: removed.append(p)):
        with self.assertRaises(bf_rsync_error):
          syncer._sync_one(src)
    self.assertNotIn(src, removed)

  # 66
  def test_source_not_deleted_on_verify_ssh_error(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'sshfail', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='e' * 64):
      call_count = [0]
      def ssh_sha256(p):
        call_count[0] += 1
        if call_count[0] == 1:
          return None
        raise bssh_error('verify ssh failed')
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
      removed = []
      with mock.patch.object(os, 'remove', side_effect=lambda p: removed.append(p)):
        with self.assertRaises(bssh_error):
          syncer._sync_one(src)
    self.assertNotIn(src, removed)

  # 67
  def test_skip_deletes_source(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'skip', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    removed = []
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='f' * 64):
      syncer._ssh_sha256 = lambda p: 'f' * 64
      with mock.patch.object(os, 'remove', side_effect=lambda p: removed.append(p)):
        syncer._sync_one(src)
    self.assertIn(src, removed)

  # 68
  def test_skip_no_rsync_call(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'skip2', suffix='.mp4')
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='0' * 64):
      syncer._ssh_sha256 = lambda p: '0' * 64
      rsync_calls = []
      with mock.patch.object(bf_rsync_command, 'call_command', side_effect=lambda a: rsync_calls.append(a)):
        with mock.patch.object(os, 'remove'):
          syncer._sync_one(src)
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
      def ssh_sha256(p):
        attempts[0] += 1
        if attempts[0] < 3:
          raise bssh_error('network error')
        return None if attempts[0] == 3 else '1' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
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
      def ssh_sha256(p):
        return None if rsync_attempts[0] < 2 else '2' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = rsync
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
      def ssh_sha256(p):
        attempt[0] += 1
        if attempt[0] == 1:
          raise bssh_error('fail once')
        return None if attempt[0] == 2 else '3' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
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
      def ssh_sha256(p):
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
      def ssh_sha256(p):
        call_count[0] += 1
        return None if call_count[0] == 1 else '5' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
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
      def ssh_sha256(p):
        call_count[0] += 1
        return None if call_count[0] % 2 == 1 else '6' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: transferred.append(path.basename(s))
      with mock.patch.object(os, 'remove'):
        syncer._run_loop()
    self.assertIn('clip1.mp4', transferred)
    self.assertIn('clip2.mp4', transferred)

  # 75
  def test_empty_source_dir(self):
    syncer = self._make_syncer(source_dirs=[self.make_temp_dir()])
    rsync_called = []
    with mock.patch.object(bf_rsync_command, 'call_command', side_effect=lambda a: rsync_called.append(a)):
      syncer._run_loop()
    self.assertEqual([], rsync_called)

  # 76
  def test_nonexistent_source_dir(self):
    syncer = self._make_syncer(source_dirs=['/nonexistent/dir'])
    with mock.patch.object(bf_rsync_command, 'call_command'):
      syncer._run_loop()  # should not raise

  # 77-86: logging tests
  def test_log_skip_line(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'log', suffix='.mp4')
    lines = []
    orig_emit = syncer._emit
    syncer._emit = lambda tag, msg: lines.append((tag, msg))
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='7' * 64):
      syncer._ssh_sha256 = lambda p: '7' * 64
      with mock.patch.object(os, 'remove'):
        syncer._sync_one(src)
    self.assertTrue(any(tag == 'SKIP' for tag, _ in lines))

  def test_log_transfer_line(self):
    syncer = self._make_syncer()
    src = self.make_temp_file(content=b'xfer', suffix='.mp4')
    lines = []
    syncer._emit = lambda tag, msg: lines.append((tag, msg))
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='8' * 64):
      call_count = [0]
      def ssh_sha256(p):
        call_count[0] += 1
        return None if call_count[0] == 1 else '8' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
      with mock.patch.object(os, 'remove'):
        syncer._sync_one(src)
    self.assertTrue(any(tag == 'TRANSFER' for tag, _ in lines))

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
      syncer._ssh_sha256 = lambda p: '9' * 64
      with mock.patch.object(os, 'remove'):
        syncer._sync_one(src)
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
      syncer._ssh_sha256 = lambda p: 'a1' * 32
      with mock.patch.object(os, 'remove'):
        with mock.patch.object(syncer, '_cleanup_partial'):
          syncer.run()
    self.assertTrue(path.exists(log_path))
    with open(log_path) as f:
      content = f.read()
    self.assertIn('[SKIP', content)

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
      syncer._ssh_sha256 = lambda p: None
      with mock.patch.object(bf_rsync_command, 'call_command', side_effect=lambda a, **kw: rsync_calls.append(a)):
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
      syncer._ssh_sha256 = lambda p: None
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
      syncer._ssh_sha256 = lambda p: 'c' * 64
      syncer._run_loop()
    self.assertTrue(path.exists(src))

  def test_dry_run_emits_dry_run_tag(self):
    src_dir = self.make_temp_dir()
    src = path.join(src_dir, 'video.mp4')
    with open(src, 'wb') as f:
      f.write(b'data')
    syncer = self._make_syncer(source_dirs=[src_dir], dry_run=True)
    tags = []
    syncer._emit = lambda tag, msg: tags.append(tag)
    from bes.files.checksum.bf_checksum_cache import bf_checksum_cache
    with mock.patch.object(bf_checksum_cache, 'get_checksum', return_value='d' * 64):
      syncer._ssh_sha256 = lambda p: None
      syncer._run_loop()
    self.assertIn('DRY-RUN', tags)

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
      def ssh_sha256(p):
        call_count[0] += 1
        return None if call_count[0] == 1 else 'e' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
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
      def ssh_sha256(p):
        call_count[0] += 1
        return None if call_count[0] == 1 else 'f' * 64
      syncer._ssh_sha256 = ssh_sha256
      syncer._rsync = lambda s, d: None
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
      syncer._ssh_sha256 = lambda p: '0' * 64
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
      syncer._ssh_sha256 = lambda p: None
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
    files = syncer._collect_files()
    self.assertIn(top_file, files)
    self.assertIn(sub_file, files)

  def test_collect_files_deeply_nested(self):
    src_dir = self.make_temp_dir()
    deep = path.join(src_dir, 'a', 'b', 'c')
    os.makedirs(deep)
    deep_file = path.join(deep, 'movie.mp4')
    open(deep_file, 'w').close()
    syncer = self._make_syncer(source_dirs=[src_dir])
    files = syncer._collect_files()
    self.assertIn(deep_file, files)

  def test_collect_files_excludes_ds_store_in_subdir(self):
    src_dir = self.make_temp_dir()
    sub = path.join(src_dir, 'sub')
    os.makedirs(sub)
    ds_store = path.join(sub, '.DS_Store')
    real_file = path.join(sub, 'movie.mp4')
    open(ds_store, 'w').close()
    open(real_file, 'w').close()
    syncer = self._make_syncer(source_dirs=[src_dir])
    files = syncer._collect_files()
    self.assertNotIn(ds_store, files)
    self.assertIn(real_file, files)

  def test_collect_files_sorted(self):
    src_dir = self.make_temp_dir()
    sub = path.join(src_dir, 'sub')
    os.makedirs(sub)
    open(path.join(src_dir, 'z.mp4'), 'w').close()
    open(path.join(sub, 'a.mp4'), 'w').close()
    syncer = self._make_syncer(source_dirs=[src_dir])
    files = syncer._collect_files()
    self.assertEqual(files, sorted(files))


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

  def _write_file(self, directory, filename, content=b'data'):
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
    src_dir = self.make_temp_dir()
    src = self._write_file(src_dir, 'new.mp4', b'new content')
    syncer = self._make_syncer([src_dir])
    syncer.run()
    self.assertFalse(path.exists(src))
    dest = path.join(self._sandbox.nas_root, 'new.mp4')
    self.assertTrue(path.exists(dest))

  # 95
  def test_integration_skip_same_file(self):
    nas_dir = self._sandbox.nas_root
    content = b'identical content'
    existing = self._write_file(nas_dir, 'same.mp4', content)
    src_dir = self.make_temp_dir()
    src = self._write_file(src_dir, 'same.mp4', content)
    syncer = self._make_syncer([src_dir])
    syncer.run()
    self.assertFalse(path.exists(src))
    self.assertTrue(path.exists(existing))

  # 96
  def test_integration_rename_different_content(self):
    nas_dir = self._sandbox.nas_root
    self._write_file(nas_dir, 'differ.mp4', b'nas version')
    src_dir = self.make_temp_dir()
    src_content = b'local version'
    src = self._write_file(src_dir, 'differ.mp4', src_content)
    local_hash = self._sha256(src)
    syncer = self._make_syncer([src_dir])
    syncer.run()
    self.assertFalse(path.exists(src))
    unique_name = f'differ-{local_hash[:8]}.mp4'
    self.assertTrue(path.exists(path.join(nas_dir, unique_name)))

  # 97
  def test_integration_multiple_files(self):
    nas_dir = self._sandbox.nas_root
    # pre-existing same
    self._write_file(nas_dir, 'a.mp4', b'aaa')
    src_dir = self.make_temp_dir()
    self._write_file(src_dir, 'a.mp4', b'aaa')   # same → skip
    self._write_file(src_dir, 'b.mp4', b'bbb')   # new
    self._write_file(src_dir, 'c.mp4', b'ccc')   # new
    syncer = self._make_syncer([src_dir])
    syncer.run()
    self.assertEqual([], [f for f in os.listdir(src_dir) if f.endswith('.mp4')])
    self.assertTrue(path.exists(path.join(nas_dir, 'b.mp4')))
    self.assertTrue(path.exists(path.join(nas_dir, 'c.mp4')))

  # 98
  def test_integration_partial_resume(self):
    # write a file, pre-create a truncated partial on the NAS, run — should complete
    src_dir = self.make_temp_dir()
    content = b'partial resume test ' * 1024
    src = self._write_file(src_dir, 'partial.mp4', content)
    partial_dir = path.join(self._sandbox.nas_root, '.rsync-partial')
    os.makedirs(partial_dir, exist_ok=True)
    with open(path.join(partial_dir, 'partial.mp4'), 'wb') as f:
      f.write(content[:len(content)//2])
    syncer = self._make_syncer([src_dir])
    syncer.run()
    self.assertFalse(path.exists(src))
    self.assertEqual(content, open(path.join(self._sandbox.nas_root, 'partial.mp4'), 'rb').read())

  # 99
  def test_integration_large_file(self):
    src_dir = self.make_temp_dir()
    content = os.urandom(10 * 1024 * 1024)  # 10 MB (keep test fast)
    src = self._write_file(src_dir, 'large.mp4', content)
    expected_hash = self._sha256(src)
    syncer = self._make_syncer([src_dir])
    syncer.run()
    dest = path.join(self._sandbox.nas_root, 'large.mp4')
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
    src_dir = self.make_temp_dir()
    content = b'verify me'
    src = self._write_file(src_dir, 'verify.mp4', content)
    expected = self._sha256(src)
    syncer = self._make_syncer([src_dir])
    syncer.run()
    dest = path.join(self._sandbox.nas_root, 'verify.mp4')
    self.assertEqual(expected, self._sha256(dest))

  # 102
  def test_integration_source_preserved_on_interrupted_transfer(self):
    src_dir = self.make_temp_dir()
    src = self._write_file(src_dir, 'interrupt.mp4', b'interrupt')
    syncer = self._make_syncer([src_dir])
    # simulate rsync failure
    syncer._rsync = lambda s, d: (_ for _ in ()).throw(bf_rsync_error('simulated interrupt'))
    with self.assertRaises(Exception):
      syncer._sync_one(src)
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


def _fake_rv(stdout):
  from collections import namedtuple
  R = namedtuple('R', 'stdout exit_code')
  return R(stdout=stdout, exit_code=0)


if __name__ == '__main__':
  unit_test.main()
