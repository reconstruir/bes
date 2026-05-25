#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.media_finder.bf_media_finder_options import bf_media_finder_options
from bes.files.media_finder.bf_media_sort_type import bf_media_sort_type
from bes.system.check import check

class test_bf_media_finder_options(unit_test):

  def test_defaults(self):
    o = bf_media_finder_options()
    self.assertEqual(frozenset(['image', 'video']), o.media_types)
    self.assertEqual(bf_media_sort_type.FOUND_ORDER, o.sort_type)
    self.assertEqual('.bes_ignore', o.ignore_file)
    self.assertFalse(o.case_sensitive)

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

  def test_ignore_file_custom(self):
    o = bf_media_finder_options(ignore_file='.myignore')
    self.assertEqual('.myignore', o.ignore_file)

  def test_check_register(self):
    o = bf_media_finder_options()
    self.assertEqual(o, check.check_bf_media_finder_options(o))

if __name__ == '__main__':
  unit_test.main()
