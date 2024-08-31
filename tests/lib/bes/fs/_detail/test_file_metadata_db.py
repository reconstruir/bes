#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs._detail.file_metadata_db import file_metadata_db
from bes.fs.file_metadata import file_metadata
from bes.fs.file_util import file_util
from bes.key_value.key_value_list import key_value_list

from unittest.mock import Mock, MagicMock, call

class test_file_metadata(unit_test):

  def setUp(self):
    # Mock the database connection and logger
    self.mock_db = Mock()
    self.mock_log = Mock()
    file_metadata_db.log = self.mock_log
    self.db_instance = file_metadata_db(self.mock_db)
    
  def test_sqlite_write_commit_success(self):
    # Mock function to simulate a successful DB operation
    mock_function = Mock()
    
    self.db_instance._sqlite_write('test_label', mock_function, 'arg1', 'arg2')
    
    mock_function.assert_called_once_with('arg1', 'arg2')
    self.mock_db.commit.assert_called_once()
    self.mock_log.log_e.assert_not_called()
    self.mock_log.log_exception.assert_not_called()

  def test_sqlite_write_exception_rollback_success(self):
    # Mock function to raise an exception during the DB operation
    mock_function = Mock(side_effect=Exception('Test exception'))
    
    with self.assertRaises(Exception):
      self.db_instance._sqlite_write('test_label', mock_function, 'arg1')
    
    mock_function.assert_called_once_with('arg1')
    self.mock_db.commit.assert_not_called()
    self.mock_db.rollback.assert_called_once()
    self.mock_log.log_e.assert_called_once()
    self.mock_log.log_exception.assert_called_once()
    self.mock_log.log_i.assert_called_once_with('test_label: Rollback successful')

  def xtest_sqlite_write_exception_rollback_failure(self):
    # Mock function to raise an exception during the DB operation
    mock_function = Mock(side_effect=Exception('Test exception'))
    # Mock rollback to also raise an exception
    self.mock_db.rollback.side_effect = Exception('Rollback failed')
    
    with self.assertRaises(Exception):
      self.db_instance._sqlite_write('test_label', mock_function, 'arg1')
    
    mock_function.assert_called_once_with('arg1')
    self.mock_db.commit.assert_not_called()
    self.mock_db.rollback.assert_called_once()
    self.mock_log.log_e.assert_called()
    self.mock_log.log_exception.assert_has_calls([call(Exception('Test exception')), call(Exception('Rollback failed'))])
    
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
    self.assertEqual( True, db._db._db.has_table(db._table_name('something', tmp_file)) )
    db.clear('something', tmp_file)
    self.assertEqual( [], db.get_values('something', tmp_file) )
    self.assertEqual( False, db._db._db.has_table(db._table_name('something', tmp_file)) )
    
if __name__ == '__main__':
  unit_test.main()
    
