#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.fingerprint.bf_fingerprint_hashlib import bf_fingerprint_hashlib
from bes.common.hash_util import hash_util

class test_bf_fingerprint_hashlib(unit_test):

  def test_checksum_sha256(self):
    f = bf_fingerprint_hashlib()
    content = 'this is kiwi'
    tmp = self.make_temp_file(content = content)
    actual = f.checksum_sha256(tmp)
    self.assertEqual( hash_util.hash_string_sha256(content), actual )

  def test_checksum_md5(self):
    f = bf_fingerprint_hashlib()
    content = 'this is kiwi'
    tmp = self.make_temp_file(content = content)
    actual = f.checksum_md5(tmp)
    self.assertEqual( hash_util.hash_string_md5(content), actual )

  def test_checksum_sha512(self):
    f = bf_fingerprint_hashlib()
    content = 'this is kiwi'
    tmp = self.make_temp_file(content = content)
    actual = f.checksum_sha512(tmp)

  def test_checksum_sha256_with_one_chunk(self):
    f = bf_fingerprint_hashlib()
    content = 'this is kiwi'
    tmp = self.make_temp_file(content = content)
    actual = f.checksum_sha256(tmp, chunk_size = 4, num_chunks = 1)
    self.assertEqual( hash_util.hash_string_sha256('this'), actual )

  def test_checksum_sha256_with_two_chunks(self):
    f = bf_fingerprint_hashlib()
    content = 'this is kiwi'
    tmp = self.make_temp_file(content = content)
    actual = f.checksum_sha256(tmp, chunk_size = 4, num_chunks = 2)
    self.assertEqual( hash_util.hash_string_sha256('this is '), actual )

  def test_checksum_sha256_with_two_chunks(self):
    f = bf_fingerprint_hashlib()
    content = 'this is kiwi'
    tmp = self.make_temp_file(content = content)
    actual = f.checksum_sha256(tmp, chunk_size = 4, num_chunks = 2)
    self.assertEqual( hash_util.hash_string_sha256('this is '), actual )

  def test_checksum_short_sha_matches_first_chunk(self):
    f = bf_fingerprint_hashlib()
    content = 'abcdefghij' * 200000  # make file > 2MB
    tmp = self.make_temp_file(content = content)

    # checksum_short_sha should equal checksum of first SHORT_CHECKSUM_SIZE bytes
    first_part = content[:f.SHORT_CHECKSUM_SIZE]
    expected = hash_util.hash_string_sha256(first_part)
    actual = f.checksum_short_sha(tmp, 'sha256')
    self.assertEqual( expected, actual )

  def test_checksum_short_sha_small_file(self):
    f = bf_fingerprint_hashlib()
    content = 'tiny file'
    tmp = self.make_temp_file(content = content)

    # for small files, short checksum == full checksum
    expected = hash_util.hash_string_sha256(content)
    actual = f.checksum_short_sha(tmp, 'sha256')
    self.assertEqual( expected, actual )
    
if __name__ == '__main__':
  unit_test.main()
