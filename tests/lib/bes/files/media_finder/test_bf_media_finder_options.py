#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.media_finder.bf_media_attr_resolver_base import bf_media_attr_resolver_base
from bes.files.media_finder.bf_media_finder_options import bf_media_finder_options
from bes.files.media_finder.bf_media_sort_type import bf_media_sort_type
from bes.system.check import check

class _FakeResolver(bf_media_attr_resolver_base):
  name = '_test_fake_resolver_options'
  @classmethod
  def resolve(cls, filename, mime_type, attr_name):
    return None

class test_bf_media_finder_options(unit_test):

  def test_defaults(self):
    o = bf_media_finder_options()
    self.assertEqual(frozenset(['image', 'video']), o.media_types)
    self.assertEqual(bf_media_sort_type.FOUND_ORDER, o.sort_type)
    self.assertEqual('.bes_ignore', o.ignore_file)
    self.assertFalse(o.case_sensitive)
    self.assertFalse(o.sort_reversed)
    self.assertIsNone(o.attr_resolver)
    self.assertEqual(2,  o.num_scan_workers)
    self.assertEqual(50, o.scan_chunk_size)
    self.assertEqual(2,  o.num_resolve_workers)
    self.assertEqual(10, o.resolve_chunk_size)

  def test_media_types_image(self):
    o = bf_media_finder_options(media_types='image')
    self.assertEqual(frozenset(['image']), o.media_types)

  def test_media_types_video(self):
    o = bf_media_finder_options(media_types='video')
    self.assertEqual(frozenset(['video']), o.media_types)

  def test_media_types_all(self):
    o = bf_media_finder_options(media_types='all')
    self.assertEqual(frozenset(['image', 'video']), o.media_types)

  def test_sort_type_name(self):
    o = bf_media_finder_options(sort_type='name')
    self.assertEqual(bf_media_sort_type.NAME, o.sort_type)

  def test_sort_type_date(self):
    o = bf_media_finder_options(sort_type='date')
    self.assertEqual(bf_media_sort_type.DATE, o.sort_type)

  def test_case_sensitive(self):
    o = bf_media_finder_options(case_sensitive=True)
    self.assertTrue(o.case_sensitive)

  def test_sort_reversed_default(self):
    o = bf_media_finder_options()
    self.assertFalse(o.sort_reversed)

  def test_sort_reversed_true(self):
    o = bf_media_finder_options(sort_reversed=True)
    self.assertTrue(o.sort_reversed)

  def test_ignore_file_custom(self):
    o = bf_media_finder_options(ignore_file='.myignore')
    self.assertEqual('.myignore', o.ignore_file)

  def test_scan_chunk_size_custom(self):
    o = bf_media_finder_options(scan_chunk_size=5)
    self.assertEqual(5, o.scan_chunk_size)

  def test_resolve_chunk_size_custom(self):
    o = bf_media_finder_options(resolve_chunk_size=3)
    self.assertEqual(3, o.resolve_chunk_size)

  def test_num_scan_workers_custom(self):
    o = bf_media_finder_options(num_scan_workers=4)
    self.assertEqual(4, o.num_scan_workers)

  def test_num_resolve_workers_custom(self):
    o = bf_media_finder_options(num_resolve_workers=8)
    self.assertEqual(8, o.num_resolve_workers)

  def test_attr_resolver_class(self):
    o = bf_media_finder_options(attr_resolver=_FakeResolver)
    self.assertIs(_FakeResolver, o.attr_resolver)

  def test_sort_type_extended_string(self):
    o = bf_media_finder_options(sort_type='resolution')
    self.assertEqual('resolution', o.sort_type)

  def test_check_register(self):
    o = bf_media_finder_options()
    self.assertEqual(o, check.check_bf_media_finder_options(o))

if __name__ == '__main__':
  unit_test.main()
