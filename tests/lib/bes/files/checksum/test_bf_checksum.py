#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.checksum.bf_checksum import bf_checksum
from bes.common.hash_util import hash_util

class test_bf_checksum(unit_test):

  def test_checksum_sha256(self):
    content = 'this is kiwi'
    tmp = self.make_temp_file(content = content)
    actual = bf_checksum.checksum(tmp, 'sha256')
    self.assertEqual( hash_util.hash_string_sha256(content), actual )

  def test_checksum_sha256_with_one_chunk(self):
    content = 'this is kiwi'
    tmp = self.make_temp_file(content = content)
    actual = bf_checksum.checksum(tmp, 'sha256', chunk_size = 4, num_chunks = 1)
    self.assertEqual( hash_util.hash_string_sha256('this'), actual )

  def test_checksum_sha256_with_two_chunks(self):
    content = 'this is kiwi'
    tmp = self.make_temp_file(content = content)
    actual = bf_checksum.checksum(tmp, 'sha256', chunk_size = 4, num_chunks = 2)
    self.assertEqual( hash_util.hash_string_sha256('this is '), actual )
    
if __name__ == '__main__':
  unit_test.main()
