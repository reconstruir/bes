#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.bf_size import bf_size

class test_bf_size(unit_test):

  def test_parse_size_bytes(self):
    self.assertEqual(0, bf_size.parse_size('0'))
    self.assertEqual(100, bf_size.parse_size('100'))
    self.assertEqual(1048576, bf_size.parse_size('1048576'))

  def test_parse_size_kilobytes(self):
    self.assertEqual(1024, bf_size.parse_size('1k'))
    self.assertEqual(1024, bf_size.parse_size('1K'))
    self.assertEqual(512 * 1024, bf_size.parse_size('512k'))

  def test_parse_size_megabytes(self):
    self.assertEqual(1024 ** 2, bf_size.parse_size('1m'))
    self.assertEqual(1024 ** 2, bf_size.parse_size('1M'))
    self.assertEqual(10 * 1024 ** 2, bf_size.parse_size('10M'))

  def test_parse_size_gigabytes(self):
    self.assertEqual(1024 ** 3, bf_size.parse_size('1g'))
    self.assertEqual(1024 ** 3, bf_size.parse_size('1G'))
    self.assertEqual(2 * 1024 ** 3, bf_size.parse_size('2G'))

  def test_parse_size_terabytes(self):
    self.assertEqual(1024 ** 4, bf_size.parse_size('1t'))
    self.assertEqual(1024 ** 4, bf_size.parse_size('1T'))

  def test_parse_size_with_whitespace(self):
    self.assertEqual(1024, bf_size.parse_size('  1k  '))

  def test_parse_size_invalid(self):
    with self.assertRaises(ValueError):
      bf_size.parse_size('abc')
    with self.assertRaises(ValueError):
      bf_size.parse_size('1.5M')
    with self.assertRaises(ValueError):
      bf_size.parse_size('')

if __name__ == '__main__':
  unit_test.main()
