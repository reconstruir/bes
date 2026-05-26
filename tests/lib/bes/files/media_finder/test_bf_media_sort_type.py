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

  def test_all_intrinsic_values(self):
    members = set(bf_media_sort_type)
    expected = {
      bf_media_sort_type.FOUND_ORDER,
      bf_media_sort_type.NAME,
      bf_media_sort_type.PATH,
      bf_media_sort_type.DATE,
      bf_media_sort_type.SIZE,
      bf_media_sort_type.KIND,
    }
    self.assertEqual(expected, members)

  def test_intrinsic_isinstance(self):
    for v in bf_media_sort_type:
      self.assertIsInstance(v, bf_media_sort_type)

  def test_string_not_isinstance(self):
    self.assertNotIsInstance('resolution', bf_media_sort_type)

  def test_extended_string_not_parseable(self):
    with self.assertRaises(ValueError):
      bf_media_sort_type('resolution')

  def test_parse_invalid(self):
    with self.assertRaises(ValueError):
      bf_media_sort_type.parse('notatype')

if __name__ == '__main__':
  unit_test.main()
