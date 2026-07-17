#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import hashlib

from bes.testing.unit_test import unit_test
from bes.files.fingerprint.bf_media_fingerprint import bf_media_fingerprint

class test_bf_media_fingerprint(unit_test):

  # just over the sampling threshold so the head/mid/tail path is exercised
  _LARGE_SIZE = 2 * 1024 * 1024

  def _make_large_file(self):
    tmp = self.make_temp_file()
    with open(tmp, 'wb') as f:
      f.write(bytes(range(256)) * (self._LARGE_SIZE // 256))
    bf_media_fingerprint.clear_cache()
    return tmp

  def _patch_bytes(self, filename, offset, data):
    with open(filename, 'r+b') as f:
      f.seek(offset)
      f.write(data)
    # the cache key includes mtime_ns, but clear anyway so a same-tick
    # rewrite can never serve the stale fingerprint and flake the test
    bf_media_fingerprint.clear_cache()

  def test_small_file_is_full_content_hash(self):
    content = b'this is kiwi'
    tmp = self.make_temp_file(content = content)
    expected = hashlib.sha256(len(content).to_bytes(8, 'big') + content).hexdigest()
    self.assertEqual( expected, bf_media_fingerprint.fingerprint(tmp) )

  def test_empty_file(self):
    tmp = self.make_temp_file()
    expected = hashlib.sha256((0).to_bytes(8, 'big')).hexdigest()
    self.assertEqual( expected, bf_media_fingerprint.fingerprint(tmp) )

  def test_same_content_different_paths_match(self):
    tmp1 = self.make_temp_file(content = b'this is kiwi')
    tmp2 = self.make_temp_file(content = b'this is kiwi')
    self.assertEqual( bf_media_fingerprint.fingerprint(tmp1),
                      bf_media_fingerprint.fingerprint(tmp2) )

  def test_small_file_content_change_changes_fingerprint(self):
    tmp = self.make_temp_file(content = b'this is kiwi')
    before = bf_media_fingerprint.fingerprint(tmp)
    self._patch_bytes(tmp, 0, b'T')
    self.assertNotEqual( before, bf_media_fingerprint.fingerprint(tmp) )

  def test_large_file_head_change_changes_fingerprint(self):
    tmp = self._make_large_file()
    before = bf_media_fingerprint.fingerprint(tmp)
    self._patch_bytes(tmp, 10, b'\xff' * 4)
    self.assertNotEqual( before, bf_media_fingerprint.fingerprint(tmp) )

  def test_large_file_tail_change_changes_fingerprint(self):
    tmp = self._make_large_file()
    before = bf_media_fingerprint.fingerprint(tmp)
    self._patch_bytes(tmp, self._LARGE_SIZE - 10, b'\xff' * 4)
    self.assertNotEqual( before, bf_media_fingerprint.fingerprint(tmp) )

  def test_large_file_mid_sample_change_changes_fingerprint(self):
    tmp = self._make_large_file()
    before = bf_media_fingerprint.fingerprint(tmp)
    self._patch_bytes(tmp, self._LARGE_SIZE // 2, b'\xff' * 4)
    self.assertNotEqual( before, bf_media_fingerprint.fingerprint(tmp) )

  def test_large_file_unsampled_region_change_keeps_fingerprint(self):
    'sampled identity by design: bytes between the samples do not affect the value'
    tmp = self._make_large_file()
    before = bf_media_fingerprint.fingerprint(tmp)
    # past the 64KiB head, well short of the first mid sample at size / 4
    self._patch_bytes(tmp, 200_000, b'\xff' * 4)
    self.assertEqual( before, bf_media_fingerprint.fingerprint(tmp) )

  def test_large_file_size_change_changes_fingerprint(self):
    tmp = self._make_large_file()
    before = bf_media_fingerprint.fingerprint(tmp)
    with open(tmp, 'ab') as f:
      f.write(b'x')
    bf_media_fingerprint.clear_cache()
    self.assertNotEqual( before, bf_media_fingerprint.fingerprint(tmp) )

if __name__ == '__main__':
  unit_test.main()
