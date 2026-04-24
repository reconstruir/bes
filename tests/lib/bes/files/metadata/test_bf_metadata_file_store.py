#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path

from bes.testing.unit_test import unit_test
from bes.files.metadata.bf_metadata_file_store import bf_metadata_file_store

class test_bf_metadata_file_store(unit_test):

  def _make_store(self):
    database_path = self.make_temp_file(suffix = '.db', non_existent = True)
    return bf_metadata_file_store(database_path = database_path)

  def test_set_and_get(self):
    store = self._make_store()
    tmp = self.make_temp_file(content = 'kiwi')
    store.set(tmp, 'color', 'green')
    self.assertEqual('green', store.get(tmp, 'color'))

  def test_get_missing_key(self):
    store = self._make_store()
    tmp = self.make_temp_file(content = 'kiwi')
    self.assertIsNone(store.get(tmp, 'missing'))

  def test_set_overwrites(self):
    store = self._make_store()
    tmp = self.make_temp_file(content = 'kiwi')
    store.set(tmp, 'color', 'green')
    store.set(tmp, 'color', 'yellow')
    self.assertEqual('yellow', store.get(tmp, 'color'))

  def test_survives_rename(self):
    store = self._make_store()
    tmp = self.make_temp_file(content = 'kiwi')
    store.set(tmp, 'color', 'green')

    renamed = tmp + '_renamed'
    os.rename(tmp, renamed)
    self.addCleanup(lambda: os.unlink(renamed) if path.exists(renamed) else None)

    self.assertEqual('green', store.get(renamed, 'color'))

  def test_content_change_loses_metadata(self):
    store = self._make_store()
    tmp = self.make_temp_file(content = 'kiwi')
    store.set(tmp, 'color', 'green')

    with open(tmp, 'w') as f:
      f.write('lemon')

    self.assertIsNone(store.get(tmp, 'color'))

  def test_delete_by_key(self):
    store = self._make_store()
    tmp = self.make_temp_file(content = 'kiwi')
    store.set(tmp, 'color', 'green')
    store.set(tmp, 'size', 'large')
    store.delete(tmp, 'color')
    self.assertIsNone(store.get(tmp, 'color'))
    self.assertEqual('large', store.get(tmp, 'size'))

  def test_delete_all(self):
    store = self._make_store()
    tmp = self.make_temp_file(content = 'kiwi')
    store.set(tmp, 'color', 'green')
    store.set(tmp, 'size', 'large')
    store.delete(tmp)
    self.assertIsNone(store.get(tmp, 'color'))
    self.assertIsNone(store.get(tmp, 'size'))

  def test_keys(self):
    store = self._make_store()
    tmp = self.make_temp_file(content = 'kiwi')
    store.set(tmp, 'color', 'green')
    store.set(tmp, 'size', 'large')
    store.set(tmp, 'weight', 'light')
    self.assertEqual(['color', 'size', 'weight'], store.keys(tmp))

  def test_keys_empty(self):
    store = self._make_store()
    tmp = self.make_temp_file(content = 'kiwi')
    self.assertEqual([], store.keys(tmp))

  def test_get_all(self):
    store = self._make_store()
    tmp = self.make_temp_file(content = 'kiwi')
    store.set(tmp, 'color', 'green')
    store.set(tmp, 'size', 'large')
    self.assertEqual({'color': 'green', 'size': 'large'}, store.get_all(tmp))

  def test_get_all_empty(self):
    store = self._make_store()
    tmp = self.make_temp_file(content = 'kiwi')
    self.assertEqual({}, store.get_all(tmp))

if __name__ == '__main__':
  unit_test.main()
