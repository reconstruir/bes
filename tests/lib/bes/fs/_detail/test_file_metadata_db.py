#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import hashlib
import os
import os.path as path
import subprocess
import sys
import bes
from bes.testing.unit_test import unit_test
from bes.fs._detail.file_metadata_db import file_metadata_db
from bes.fs.file_metadata import file_metadata
from bes.files.bf_file_ops import bf_file_ops
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
    
  def test_unsigned_hash_matches_sha256_not_builtin_hash(self):
    '''
    Ties _unsigned_hash() to a specific, verifiable algorithm (sha256 of
    the utf-8 filename, first 16 bytes as an int) rather than just
    asserting "it returns something" -- a regression back to Python's
    builtin hash() would still return *some* int and could slip past a
    weaker test.
    '''
    filename = 'some/file/path.txt'
    expected = int(hashlib.sha256(filename.encode('utf-8')).hexdigest()[:32], 16)
    self.assertEqual( expected, file_metadata_db._unsigned_hash(filename) )

  def test_unsigned_hash_is_stable_across_separate_processes(self):
    '''
    The actual bug this class used to have, reproduced directly: Python's
    builtin hash() on a str is randomized per-process by default
    (PYTHONHASHSEED), so a value written by one process was silently
    unreadable by another (bat's ingest_provenance marker going missing
    between separate "bat ingest run" / "bat ingest prune_store"
    invocations against a vfs_local store is what surfaced this -- see
    bat/claude-docs/build-arch-normalization.md). Spawn two real, separate
    Python processes with different PYTHONHASHSEED values and confirm
    _unsigned_hash() -- and therefore _table_name() -- computes the exact
    same value in both; this is the one thing a same-process test can
    never actually prove, since a single process only ever has one seed.
    '''
    filename = 'some/file/path.txt'
    code = (
      'from bes.fs._detail.file_metadata_db import file_metadata_db\n'
      'print(file_metadata_db._unsigned_hash({!r}))\n'
    ).format(filename)

    def _run_with_hashseed(seed):
      env = dict(os.environ)
      env['PYTHONHASHSEED'] = seed
      # bes's own lib dir -- wherever this repo actually happens to be
      # checked out, not an assumption about relative test-file depth
      env['PYTHONPATH'] = path.dirname(path.dirname(path.abspath(bes.__file__)))
      result = subprocess.run([ sys.executable, '-c', code ], env = env,
                              capture_output = True, text = True, check = True)
      return result.stdout.strip()

    hash_seed_0 = _run_with_hashseed('0')
    hash_seed_42 = _run_with_hashseed('42')
    self.assertEqual( hash_seed_0, hash_seed_42 )
    # and it must match the same deterministic value computed in *this*
    # (a third, independent) process
    self.assertEqual( str(file_metadata_db._unsigned_hash(filename)), hash_seed_0 )

if __name__ == '__main__':
  unit_test.main()
    
