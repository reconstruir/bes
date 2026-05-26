#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.media_finder.bf_media_feature_not_available import BF_FEATURE_NOT_AVAILABLE
from bes.files.media_finder.bf_media_feature_resolver_base import bf_media_feature_resolver_base

class test_bf_media_feature_resolver_base(unit_test):

  def test_int_value(self):
    self.assertEqual((0, 42), bf_media_feature_resolver_base.feature_sort_key(42))

  def test_float_value(self):
    self.assertEqual((0, 1.5), bf_media_feature_resolver_base.feature_sort_key(1.5))

  def test_tuple_value(self):
    self.assertEqual((0, (1920, 1080)), bf_media_feature_resolver_base.feature_sort_key((1920, 1080)))

  def test_none_key(self):
    self.assertEqual((1, None), bf_media_feature_resolver_base.feature_sort_key(None))

  def test_not_available_key(self):
    self.assertEqual((1, None), bf_media_feature_resolver_base.feature_sort_key(BF_FEATURE_NOT_AVAILABLE))

  def test_none_and_not_available_equal_key(self):
    self.assertEqual(
      bf_media_feature_resolver_base.feature_sort_key(None),
      bf_media_feature_resolver_base.feature_sort_key(BF_FEATURE_NOT_AVAILABLE),
    )

  def test_real_before_none(self):
    self.assertLess(
      bf_media_feature_resolver_base.feature_sort_key(42),
      bf_media_feature_resolver_base.feature_sort_key(None),
    )

  def test_real_before_not_available(self):
    self.assertLess(
      bf_media_feature_resolver_base.feature_sort_key(42),
      bf_media_feature_resolver_base.feature_sort_key(BF_FEATURE_NOT_AVAILABLE),
    )

  def test_smaller_real_before_larger(self):
    self.assertLess(
      bf_media_feature_resolver_base.feature_sort_key(1.0),
      bf_media_feature_resolver_base.feature_sort_key(2.0),
    )

  def test_tuple_ordering(self):
    self.assertLess(
      bf_media_feature_resolver_base.feature_sort_key((640, 480)),
      bf_media_feature_resolver_base.feature_sort_key((1920, 1080)),
    )

  def test_sort_list_mixed(self):
    values = [None, 3, BF_FEATURE_NOT_AVAILABLE, 1, None, 2]
    sorted_values = sorted(values, key=bf_media_feature_resolver_base.feature_sort_key)
    real = [v for v in sorted_values if v is not None and v is not BF_FEATURE_NOT_AVAILABLE]
    non_real = [v for v in sorted_values if v is None or v is BF_FEATURE_NOT_AVAILABLE]
    self.assertEqual([1, 2, 3], real)
    self.assertEqual(3, len(non_real))

if __name__ == '__main__':
  unit_test.main()
