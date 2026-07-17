#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs.checksum import checksum
from bes.fs.checksum_set import checksum_set

class test_checksum_set(unit_test):

  def test_to_dict(self):
    s = checksum_set(checksum(checksum.SHA256, 'aaa'), checksum(checksum.MD5, 'bbb'))
    self.assertEqual( {
      'sha256': ( 'sha256', 'aaa' ),
      'md5': ( 'md5', 'bbb' ),
    }, s.to_dict() )

  def test_from_dict(self):
    s = checksum_set.from_dict({
      'sha256': ( 'sha256', 'aaa' ),
      'md5': ( 'md5', 'bbb' ),
    })
    self.assertEqual( checksum('sha256', 'aaa'), s.preferred() )
    self.assertEqual( [ checksum('md5', 'bbb'), checksum('sha256', 'aaa') ], s.to_list() )

  def test_from_dict_with_lists(self):
    'values arrive as lists instead of tuples after a json round trip'
    s = checksum_set.from_dict({
      'sha256': [ 'sha256', 'aaa' ],
    })
    self.assertEqual( checksum('sha256', 'aaa'), s.preferred() )

  def test_from_dict_round_trip(self):
    s = checksum_set(checksum(checksum.SHA256, 'aaa'), checksum(checksum.SHA1, 'ccc'))
    self.assertEqual( s, checksum_set.from_dict(s.to_dict()) )

  def test_from_dict_empty(self):
    self.assertEqual( checksum_set(), checksum_set.from_dict({}) )

  def test_eq(self):
    a = checksum_set(checksum(checksum.SHA256, 'aaa'))
    b = checksum_set(checksum(checksum.SHA256, 'aaa'))
    c = checksum_set(checksum(checksum.SHA256, 'zzz'))
    self.assertEqual( a, b )
    self.assertNotEqual( a, c )

if __name__ == '__main__':
  unit_test.main()
