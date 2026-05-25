#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.media_finder.bf_media_sort_type import bf_media_sort_type

class test_bf_media_sort_type(unit_test):

  def test_parse_found_order(self):
    self.assertEqual(bf_media_sort_type.FOUND_ORDER, bf_media_sort_type.parse('found_order'))

  def test_parse_name(self):
    self.assertEqual(bf_media_sort_type.NAME, bf_media_sort_type.parse('name'))

  def test_parse_case_insensitive(self):
    self.assertEqual(bf_media_sort_type.NAME, bf_media_sort_type.parse('NAME'))

  def test_fast_types_not_slow(self):
    fast = [
      bf_media_sort_type.FOUND_ORDER,
      bf_media_sort_type.NAME,
      bf_media_sort_type.PATH,
      bf_media_sort_type.DATE,
      bf_media_sort_type.SIZE,
      bf_media_sort_type.KIND,
    ]
    for t in fast:
      self.assertFalse(t.is_slow, f'{t} should not be slow')

  def test_slow_types_are_slow(self):
    slow = [
      bf_media_sort_type.RESOLUTION,
      bf_media_sort_type.WIDTH,
      bf_media_sort_type.HEIGHT,
      bf_media_sort_type.ASPECT_RATIO,
      bf_media_sort_type.DURATION,
      bf_media_sort_type.AVERAGE_HASH,
    ]
    for t in slow:
      self.assertTrue(t.is_slow, f'{t} should be slow')

  def test_parse_invalid(self):
    with self.assertRaises(ValueError):
      bf_media_sort_type.parse('notatype')

if __name__ == '__main__':
  unit_test.main()
