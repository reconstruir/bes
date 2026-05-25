#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.testing.unit_test import unit_test
from bes.files.media_finder.bf_media_file_entry import bf_media_file_entry
from bes.system.check import check

class test_bf_media_file_entry(unit_test):

  def _make_entry(self, root_dir='/media', filename='/media/photos/a.jpg'):
    return bf_media_file_entry(
      root_dir   = root_dir,
      filename   = filename,
      size       = 1024,
      mtime      = 1700000000.0,
      extension  = 'jpg',
      mime_type  = 'image/jpeg',
      media_type = 'image',
    )

  def test_fields(self):
    e = self._make_entry()
    self.assertEqual('/media', e.root_dir)
    self.assertEqual('/media/photos/a.jpg', e.filename)
    self.assertEqual(1024, e.size)
    self.assertEqual(1700000000.0, e.mtime)
    self.assertEqual('jpg', e.extension)
    self.assertEqual('image/jpeg', e.mime_type)
    self.assertEqual('image', e.media_type)

  def test_frozen(self):
    e = self._make_entry()
    with self.assertRaises((AttributeError, TypeError)):
      e.filename = '/other.jpg'

  def test_relative_filename(self):
    e = self._make_entry(root_dir='/media', filename='/media/photos/a.jpg')
    self.assertEqual('photos/a.jpg', e.relative_filename)

  def test_relative_filename_nested(self):
    e = self._make_entry(root_dir='/media/root', filename='/media/root/sub/deep/b.png')
    self.assertEqual('sub/deep/b.png', e.relative_filename)

  def test_str_returns_absolute_filename(self):
    e = self._make_entry(filename='/media/photos/a.jpg')
    self.assertEqual('/media/photos/a.jpg', str(e))

  def test_check_register(self):
    e = self._make_entry()
    self.assertEqual(e, check.check_bf_media_file_entry(e))

  def test_equality(self):
    e1 = self._make_entry()
    e2 = self._make_entry()
    self.assertEqual(e1, e2)

  def test_inequality(self):
    e1 = self._make_entry(filename='/media/a.jpg')
    e2 = self._make_entry(filename='/media/b.jpg')
    self.assertNotEqual(e1, e2)

if __name__ == '__main__':
  unit_test.main()
