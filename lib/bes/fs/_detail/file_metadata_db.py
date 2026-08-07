#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import hashlib
from bes.system.check import check
from bes.common.string_util import string_util
from bes.key_value.key_value import key_value
from bes.key_value.key_value_list import key_value_list
from bes.system.log import logger
from bes.system.execute import execute

class table_missing_error(Exception):
  
  def __init__(self, message, what):
    super(table_missing_error, self).__init__(message)
    self.message = message
    self.what = what
    
  def __str__(self):
    return self.message

class file_metadata_db(object):

  log = logger('file_metadata_db')
  
  # "if not exists" because concurrent threads or processes race between
  # the has_table check and the create
  _METADATA_SCHEMA = '''
create table if not exists {table_name}(
  key   text primary key not null,
  value text
);
'''

  _HASH_TO_FILENAME_SCHEMA = '''
create table if not exists hash_to_filename(
  hash     text primary key not null,
  filename text
);
'''
  
  def __init__(self, db):
    self._db = db
    self._ensure_hash_to_filename_table()

  @classmethod
  def _unsigned_hash(clazz, filename):
    '''
    A stable, deterministic hash of filename -- used to name this file's
    per-"what" attribute table (_table_name(), below) and as the
    reverse-lookup key in hash_to_filename. This *must* produce the same
    value for the same filename across separate process invocations
    touching the same on-disk db: file_metadata is meant to persist
    (that is the entire point of writing it to a sqlite file rather than
    keeping it in memory), and separate bat/bes-based CLI invocations
    routinely read a db a previous, separate process wrote.

    Previously this used Python's builtin hash(filename) -- silently
    wrong for exactly that reason: CPython randomizes str hash() per
    process by default (hash randomization, on since 3.3, reseeded every
    interpreter start unless PYTHONHASHSEED is fixed), so the *same*
    filename produced a *different* table name in every new process. A
    value written by one process was therefore invisible to
    get_values()/get_value() called from any other process -- not an
    error, just a silent, empty read (has_table() on the wrong,
    never-created table name), discovered via bat's ingest_provenance
    upload marker (see bat/claude-docs/build-arch-normalization.md)
    going missing across separate "bat ingest run" / "bat ingest
    prune_store" invocations against a vfs_local store. sha256 is used
    instead purely for its determinism -- no cryptographic property is
    actually needed here, it is not exposed or security-sensitive, just
    a stable table-name suffix.
    '''
    check.check_string(filename)
    return int(hashlib.sha256(filename.encode('utf-8')).hexdigest()[:32], 16)

  @classmethod
  def _table_name(clazz, what, filename):
    return '{}_{}'.format(what, clazz._unsigned_hash(filename))

  def get_values(self, what, filename):
    check.check_string(what)
    check.check_string(filename)
    table_name = self._table_name(what, filename)
    if not self._db.has_table(table_name):
      return key_value_list()
    sql = 'select key, value from {table_name} order by key asc'.format(table_name = table_name)
    return key_value_list(self._db.select_all(sql))

  def replace_values(self, what, filename, values):
    check.check_string(what)
    check.check_string(filename)
    check.check_key_value_list(values)
    table_name = self._table_name(what, filename)
    self._ensure_hash_to_filename(filename)
    self._sqlite_write('replace_values', self._replace_values_i, table_name, values)

  def set_value(self, what, filename, key, value):
    check.check_string(what)
    check.check_string(filename)
    check.check_string(key)
    table_name = self._table_name(what, filename)
    self._ensure_hash_to_filename(filename)
    self._sqlite_write('set_value', self._set_value_i, table_name, key, value)

  def get_value(self, what, filename, key):
    check.check_string(what)
    check.check_string(filename)
    check.check_string(key)
    table_name = self._table_name(what, filename)
    if not self._db.has_table(table_name):
      return None
    sql = 'select value from {table_name} where key={key}'.format(table_name = table_name,
                                                                  key = string_util.quote(key))
    result = self._db.select_one(sql)
    if result is None:
      return None
    return result[0]

  def clear(self, what, filename):
    check.check_string(what)
    check.check_string(filename)
    table_name = self._table_name(what, filename)
    self._ensure_hash_to_filename(filename)
    self._sqlite_write('clear', self._clear_i, table_name)

  def _sqlite_write(self, label, function, *args):
    'Call a write operation to the db.'
    try:
      function(*args)
      self._db.commit()
    except Exception as ex:
      self.log.log_e('_sqlite_write: Caught exception: {}'.format(str(ex)))
      self.log.log_exception(ex)
      try:
        self._db.rollback()
        self.log.log_i('{}: Rollback successful'.format(label))
      except Exception as sqlite_ex:
        self.log.log_e('{}: CAUGHT EXCEPTION ROLLING BACK: {}'.format(label, str(sqlite_ex)))
      raise ex
  
  def _ensure_table(self, table_name):
    'Ensure that a table exists.  Does not commit.'
    if self._db.has_table(table_name):
      return
    schema = self._METADATA_SCHEMA.format(table_name = table_name)
    self._db.execute(schema)

  def _ensure_hash_to_filename(self, filename):
    h = self._unsigned_hash(filename)
    sql = 'insert or replace into hash_to_filename (hash, filename) values (?, ?)'
    values = ( str(h), filename )
    self._db.execute(sql, values)
    
  def _ensure_hash_to_filename_table(self):
    if self._db.has_table('hash_to_filename'):
      return
    self._db.execute(self._HASH_TO_FILENAME_SCHEMA)
    
  def _replace_values_i(self, table_name, values):
    'Do the replace_values work without transactions.'
    if not values and not self._db.has_table(table_name):
      return
    if not values:
      sql = 'delete from {table_name}'.format(table_name = table_name)
      self._db.execute(sql)
      return
    self._ensure_table(table_name)
    for kv in values:
      sql = 'insert or replace into {table_name} (key, value) values (?, ?)'.format(table_name = table_name)
      self._db.execute(sql, kv)
      keys = self._quoted_keys(values)
      sql = 'delete from {table_name} where key not in ({keys})'.format(table_name = table_name,
                                                                        keys = ', '.join(keys))
      self._db.execute(sql)
    
  def _clear_i(self, table_name):
    if not self._db.has_table(table_name):
      return
    sql = 'drop table {table_name}'.format(table_name = table_name)
    self._db.execute(sql)
    
  def _set_value_i(self, table_name, key, value):
    'Do the replace_values work without transactions.'
    self._ensure_table(table_name)
    sql = 'insert or replace into {table_name} (key, value) values (?, ?)'.format(table_name = table_name)
    self._db.execute(sql, ( key, value ))
    
  @classmethod
  def _quoted_keys(clazz, kvl):
    return [ string_util.quote(key) for key in kvl.all_keys() ]
  
