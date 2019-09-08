#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs.detail.file_metadata_db import file_metadata_db
from bes.fs.file_metadata import file_metadata
from bes.fs.file_util import file_util
from bes.key_value.key_value_list import key_value_list

class test_file_metadata(unit_test):

  def test_get_values_empty(self):
    tmp_dir = self.make_temp_dir()
    db = file_metadata(tmp_dir)
    tmp_file = self.make_temp_file(dir = tmp_dir, suffix = '.txt', content = 'this is foo\n')
    self.assertEqual( [], db.get_values('something', tmp_file) )
    self.assertEqual( False, db._db._db.has_table(db._table_name('something', tmp_file)) )
    
  def test_replace_values_from_empty(self):
    tmp_dir = self.make_temp_dir()
    db = file_metadata(tmp_dir)
    tmp_file = self.make_temp_file(dir = tmp_dir, suffix = '.txt', content = 'this is foo\n')
    self.assertEqual( [], db.get_values('something', tmp_file) )
    values = key_value_list( [ ( 'foo', 'hi' ), ( 'bar', '42' ) ] )
    db.replace_values('something', tmp_file, values)
    self.assertEqual( sorted(values), db.get_values('something', tmp_file) )

  def test_replace_values_replace(self):
    tmp_dir = self.make_temp_dir()
    db = file_metadata(tmp_dir)
    tmp_file = self.make_temp_file(dir = tmp_dir, suffix = '.txt', content = 'this is foo\n')
    self.assertEqual( [], db.get_values('something', tmp_file) )
    values1 = key_value_list( [ ( 'foo', 'hi' ), ( 'bar', '42' ) ] )
    db.replace_values('something', tmp_file, values1)
    self.assertEqual( sorted(values1), db.get_values('something', tmp_file) )

    values2 = key_value_list( [ ( 'foo', 'bye' ), ( 'bar', '666' ) ] )
    db.replace_values('something', tmp_file, values2)
    self.assertEqual( sorted(values2), db.get_values('something', tmp_file) )
    
  def test_replace_values_delete_one(self):
    tmp_dir = self.make_temp_dir()
    db = file_metadata(tmp_dir)
    tmp_file = self.make_temp_file(dir = tmp_dir, suffix = '.txt', content = 'this is foo\n')
    self.assertEqual( [], db.get_values('something', tmp_file) )
    values1 = key_value_list( [ ( 'foo', 'hi' ), ( 'bar', '42' ) ] )
    db.replace_values('something', tmp_file, values1)
    self.assertEqual( sorted(values1), db.get_values('something', tmp_file) )

    values2 = key_value_list( [ ( 'foo', 'bye' ) ] )
    db.replace_values('something', tmp_file, values2)
    self.assertEqual( sorted(values2), db.get_values('something', tmp_file) )

  def test_set_value_from_empty(self):
    tmp_dir = self.make_temp_dir()
    db = file_metadata(tmp_dir)
    tmp_file = self.make_temp_file(dir = tmp_dir, suffix = '.txt', content = 'this is foo\n')
    db.set_value('something', tmp_file, 'foo', 'hi')
    self.assertEqual( [ ( 'foo', 'hi', ) ], db.get_values('something', tmp_file) )

  def test_get_value_empty(self):
    tmp_dir = self.make_temp_dir()
    db = file_metadata(tmp_dir)
    tmp_file = self.make_temp_file(dir = tmp_dir, suffix = '.txt', content = 'this is foo\n')
    self.assertEqual( None, db.get_value('something', tmp_file, 'foo') )
    self.assertEqual( False, db._db._db.has_table(db._table_name('something', tmp_file)) )
    
  def test_get_value(self):
    tmp_dir = self.make_temp_dir()
    db = file_metadata(tmp_dir)
    tmp_file = self.make_temp_file(dir = tmp_dir, suffix = '.txt', content = 'this is foo\n')
    db.set_value('something', tmp_file, 'foo', 'hi')
    self.assertEqual( 'hi', db.get_value('something', tmp_file, 'foo') )
    
  def test_get_value_none(self):
    tmp_dir = self.make_temp_dir()
    db = file_metadata(tmp_dir)
    tmp_file = self.make_temp_file(dir = tmp_dir, suffix = '.txt', content = 'this is foo\n')
    db.set_value('something', tmp_file, 'foo', 'hi')
    self.assertEqual( 'hi', db.get_value('something', tmp_file, 'foo') )
    db.set_value('something', tmp_file, 'foo', None)
    self.assertEqual( None, db.get_value('something', tmp_file, 'foo') )
    
  def test_clear(self):
    tmp_dir = self.make_temp_dir()
    db = file_metadata(tmp_dir)
    tmp_file = self.make_temp_file(dir = tmp_dir, suffix = '.txt', content = 'this is foo\n')
    db.set_value('something', tmp_file, 'foo', 'hi')
    db.set_value('something', tmp_file, 'bar', '67')
    self.assertEqual( 'hi', db.get_value('something', tmp_file, 'foo') )
    self.assertEqual( '67', db.get_value('something', tmp_file, 'bar') )
    print('  tmp_file: {}'.format(tmp_file))
    print('table_name: {}'.format(db._table_name('something', tmp_file)))
    self.assertEqual( True, db._db._db.has_table(db._table_name('something', tmp_file)) )
    db.clear('something', tmp_file)
    self.assertEqual( [], db.get_values('something', tmp_file) )
    self.assertEqual( False, db._db._db.has_table(db._table_name('something', tmp_file)) )
    
if __name__ == '__main__':
  unit_test.main()
    
