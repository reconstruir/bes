#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime

from os import path

from bes.fs.file_util import file_util
from bes.testing.unit_test import unit_test

from bes.files.attr.bf_attr2_sql_db import bf_attr2_sql_db

class test_bf_attr2_sql_db(unit_test):

  def _make_tmp_db(self):
    tmp_db_filename = path.join(self.make_temp_dir(), 'test.db')
    return bf_attr2_sql_db(tmp_db_filename)

  def test_set_get_bytes(self):
    db = self._make_tmp_db()
    value = 'kiwi'.encode('utf-8')
    db.set_bytes('hash_666', 'fruit', value)
    self.assertEqual( value, db.get_bytes('hash_666', 'fruit') )

  def test_has_attribute_false(self):
    db = self._make_tmp_db()
    self.assertEqual( False, db.has_attribute('hash_666', 'notthere') )

  def test_has_attribute_true(self):
    db = self._make_tmp_db()
    db.set_bytes('hash_666', 'fruit', 'kiwi'.encode('utf-8'))
    self.assertEqual( False, db.has_attribute('hash_666', 'notthere') )

  def test_remove(self):
    db = self._make_tmp_db()
    self.assertEqual( False, db.has_attribute('hash_666', 'fruit') )
    db.set_bytes('hash_666', 'fruit', 'kiwi'.encode('utf-8'))
    self.assertEqual( True, db.has_attribute('hash_666', 'fruit') )
    db.remove('hash_666', 'fruit')
    self.assertEqual( False, db.has_attribute('hash_666', 'fruit') )

  def test_all_attributes(self):
    db = self._make_tmp_db()
    self.assertEqual( (), db.all_attributes('hash_666') )
    db.set_bytes('hash_666', 'fruit', 'kiwi'.encode('utf-8'))
    self.assertEqual( ( 'fruit', ), db.all_attributes('hash_666') )
    db.set_bytes('hash_666', 'cheese', 'brie'.encode('utf-8'))
    self.assertEqual( ( 'cheese', 'fruit', ), db.all_attributes('hash_666') )

  def test_clear(self):
    db = self._make_tmp_db()
    db.set_bytes('hash_666', 'fruit', 'kiwi'.encode('utf-8'))
    db.set_bytes('hash_666', 'cheese', 'brie'.encode('utf-8'))
    db.clear('hash_666')
    self.assertEqual( (), db.all_attributes('hash_666') )
    
if __name__ == '__main__':
  unit_test.main()
