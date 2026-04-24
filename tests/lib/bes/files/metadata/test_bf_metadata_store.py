#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.metadata.bf_metadata_store import bf_metadata_store

class test_bf_metadata_store(unit_test):

  def _make_store(self):
    database_path = self.make_temp_file(suffix = '.db', non_existent = True)
    return bf_metadata_store(database_path = database_path)

  def test_set_and_get(self):
    store = self._make_store()
    store.set('abc123', 'color', 'blue')
    self.assertEqual('blue', store.get('abc123', 'color'))

  def test_get_missing_checksum(self):
    store = self._make_store()
    self.assertIsNone(store.get('no_such_checksum', 'color'))

  def test_get_missing_key(self):
    store = self._make_store()
    store.set('abc123', 'color', 'blue')
    self.assertIsNone(store.get('abc123', 'missing'))

  def test_set_overwrites(self):
    store = self._make_store()
    store.set('abc123', 'color', 'blue')
    store.set('abc123', 'color', 'red')
    self.assertEqual('red', store.get('abc123', 'color'))

  def test_delete_by_key(self):
    store = self._make_store()
    store.set('abc123', 'color', 'blue')
    store.set('abc123', 'size', 'large')
    store.delete('abc123', 'color')
    self.assertIsNone(store.get('abc123', 'color'))
    self.assertEqual('large', store.get('abc123', 'size'))

  def test_delete_all_keys(self):
    store = self._make_store()
    store.set('abc123', 'color', 'blue')
    store.set('abc123', 'size', 'large')
    store.delete('abc123')
    self.assertIsNone(store.get('abc123', 'color'))
    self.assertIsNone(store.get('abc123', 'size'))

  def test_keys(self):
    store = self._make_store()
    store.set('abc123', 'color', 'blue')
    store.set('abc123', 'size', 'large')
    store.set('abc123', 'weight', 'heavy')
    self.assertEqual(['color', 'size', 'weight'], store.keys('abc123'))

  def test_keys_empty(self):
    store = self._make_store()
    self.assertEqual([], store.keys('no_such_checksum'))

  def test_get_all(self):
    store = self._make_store()
    store.set('abc123', 'color', 'blue')
    store.set('abc123', 'size', 'large')
    self.assertEqual({'color': 'blue', 'size': 'large'}, store.get_all('abc123'))

  def test_get_all_empty(self):
    store = self._make_store()
    self.assertEqual({}, store.get_all('no_such_checksum'))

if __name__ == '__main__':
  unit_test.main()
