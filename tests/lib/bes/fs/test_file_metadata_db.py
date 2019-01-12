#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs.detail.file_metadata_db import file_metadata_db
from bes.fs.file_metadata import file_metadata
from bes.fs import file_util, temp_file
from bes.sqlite import sqlite
from bes.key_value import key_value_list

class test_file_metadata(unit_test):

  def test_get_values_empty(self):
    tmp_db = temp_file.make_temp_file(suffix = '.sqlite.db')
    db = file_metadata(tmp_db)
    tmp_file = temp_file.make_temp_file(suffix = '.txt', content = 'this is foo\n')
    self.assertEqual( [], db.get_values(tmp_file) )
    self.assertEqual( False, db._db._db.has_table(db._db._table_name(tmp_file)) )
    
  def test_replace_values_from_empty(self):
    tmp_db = temp_file.make_temp_file(suffix = '.sqlite.db')
    db = file_metadata(tmp_db)
    tmp_file = temp_file.make_temp_file(suffix = '.txt', content = 'this is foo\n')
    self.assertEqual( [], db.get_values(tmp_file) )
    values = key_value_list( [ ( 'foo', 'hi' ), ( 'bar', '42' ) ] )
    db.replace_values(tmp_file, values)
    self.assertEqual( sorted(values), db.get_values(tmp_file) )

  def test_replace_values_replace(self):
    tmp_db = temp_file.make_temp_file(suffix = '.sqlite.db')
    db = file_metadata(tmp_db)
    tmp_file = temp_file.make_temp_file(suffix = '.txt', content = 'this is foo\n')
    self.assertEqual( [], db.get_values(tmp_file) )
    values1 = key_value_list( [ ( 'foo', 'hi' ), ( 'bar', '42' ) ] )
    db.replace_values(tmp_file, values1)
    self.assertEqual( sorted(values1), db.get_values(tmp_file) )

    values2 = key_value_list( [ ( 'foo', 'bye' ), ( 'bar', '666' ) ] )
    db.replace_values(tmp_file, values2)
    self.assertEqual( sorted(values2), db.get_values(tmp_file) )
    
  def test_replace_values_delete_one(self):
    tmp_db = temp_file.make_temp_file(suffix = '.sqlite.db')
    db = file_metadata(tmp_db)
    tmp_file = temp_file.make_temp_file(suffix = '.txt', content = 'this is foo\n')
    self.assertEqual( [], db.get_values(tmp_file) )
    values1 = key_value_list( [ ( 'foo', 'hi' ), ( 'bar', '42' ) ] )
    db.replace_values(tmp_file, values1)
    self.assertEqual( sorted(values1), db.get_values(tmp_file) )

    values2 = key_value_list( [ ( 'foo', 'bye' ) ] )
    db.replace_values(tmp_file, values2)
    self.assertEqual( sorted(values2), db.get_values(tmp_file) )

  def test_set_value_from_empty(self):
    tmp_db = temp_file.make_temp_file(suffix = '.sqlite.db')
    db = file_metadata(tmp_db)
    tmp_file = temp_file.make_temp_file(suffix = '.txt', content = 'this is foo\n')
    db.set_value(tmp_file, 'foo', 'hi')
    self.assertEqual( [ ( 'foo', 'hi', ) ], db.get_values(tmp_file) )

  def test_get_value_empty(self):
    tmp_db = temp_file.make_temp_file(suffix = '.sqlite.db')
    db = file_metadata(tmp_db)
    tmp_file = temp_file.make_temp_file(suffix = '.txt', content = 'this is foo\n')
    self.assertEqual( None, db.get_value(tmp_file, 'foo') )
    self.assertEqual( False, db._db._db.has_table(db._db._table_name(tmp_file)) )
    
  def test_get_value(self):
    tmp_db = temp_file.make_temp_file(suffix = '.sqlite.db')
    db = file_metadata(tmp_db)
    tmp_file = temp_file.make_temp_file(suffix = '.txt', content = 'this is foo\n')
    db.set_value(tmp_file, 'foo', 'hi')
    self.assertEqual( 'hi', db.get_value(tmp_file, 'foo') )
    
  def test_get_value_none(self):
    tmp_db = temp_file.make_temp_file(suffix = '.sqlite.db')
    db = file_metadata(tmp_db)
    tmp_file = temp_file.make_temp_file(suffix = '.txt', content = 'this is foo\n')
    db.set_value(tmp_file, 'foo', 'hi')
    self.assertEqual( 'hi', db.get_value(tmp_file, 'foo') )
    db.set_value(tmp_file, 'foo', None)
    self.assertEqual( None, db.get_value(tmp_file, 'foo') )
    
  def test_clear(self):
    tmp_db = temp_file.make_temp_file(suffix = '.sqlite.db')
    db = file_metadata(tmp_db)
    tmp_file = temp_file.make_temp_file(suffix = '.txt', content = 'this is foo\n')
    db.set_value(tmp_file, 'foo', 'hi')
    db.set_value(tmp_file, 'bar', '67')
    self.assertEqual( 'hi', db.get_value(tmp_file, 'foo') )
    self.assertEqual( '67', db.get_value(tmp_file, 'bar') )
    self.assertEqual( True, db._db._db.has_table(db._db._table_name(tmp_file)) )
    db.clear(tmp_file)
    self.assertEqual( [], db.get_values(tmp_file) )
    self.assertEqual( False, db._db._db.has_table(db._db._table_name(tmp_file)) )
    
if __name__ == '__main__':
  unit_test.main()
    
