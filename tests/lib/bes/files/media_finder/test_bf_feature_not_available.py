#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.media_finder.bf_media_feature_not_available import BF_FEATURE_NOT_AVAILABLE, _bf_feature_not_available_type

class test_bf_feature_not_available(unit_test):

  def test_is_not_none(self):
    self.assertIsNotNone(BF_FEATURE_NOT_AVAILABLE)

  def test_is_singleton(self):
    a = _bf_feature_not_available_type()
    b = _bf_feature_not_available_type()
    self.assertIs(a, b)
    self.assertIs(a, BF_FEATURE_NOT_AVAILABLE)

  def test_is_falsy(self):
    self.assertFalse(bool(BF_FEATURE_NOT_AVAILABLE))

  def test_not_equal_to_zero(self):
    self.assertNotEqual(BF_FEATURE_NOT_AVAILABLE, 0)

  def test_not_equal_to_false(self):
    self.assertNotEqual(BF_FEATURE_NOT_AVAILABLE, False)

  def test_isinstance(self):
    self.assertIsInstance(BF_FEATURE_NOT_AVAILABLE, _bf_feature_not_available_type)

  def test_repr_nonempty(self):
    self.assertTrue(len(repr(BF_FEATURE_NOT_AVAILABLE)) > 0)

if __name__ == '__main__':
  unit_test.main()
