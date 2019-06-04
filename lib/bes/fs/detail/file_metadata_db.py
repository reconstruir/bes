#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
from bes.common.check import check
from bes.common.string_util import string_util
from bes.key_value.key_value import key_value
from bes.key_value.key_value_list import key_value_list

class table_missing_error(Exception):
  
  def __init__(self, message, what):
    super(table_missing_error, self).__init__(message)
    self.message = message
    self.what = what
    
  def __str__(self):
    return self.message

class file_metadata_db(object):

  _METADATA_SCHEMA = '''
create table {table_name}(
  key                 text primary key not null,
  value               text
);
'''
  
  def __init__(self, db):
    self._db = db

  @classmethod
  def _unsigned_hash(clazz, filename):
    check.check_string(filename)
    return hash(filename) + sys.maxsize
    
  @classmethod
  def _table_name(clazz, filename):
    return 'file_%d' % (clazz._unsigned_hash(filename))

  def get_values(self, filename):
    check.check_string(filename)
    table_name = self._table_name(filename)
    if not self._db.has_table(table_name):
      return key_value_list()
    sql = 'select key, value from {table_name} order by key asc'.format(table_name = table_name)
    return key_value_list(self._db.select_all(sql))

  def replace_values(self, filename, values):
    check.check_string(filename)
    check.check_key_value_list(values)
    table_name = self._table_name(filename)
    self._call_sqlite('replace_values', self._replace_values_i, table_name, values)

  def set_value(self, filename, key, value):
    check.check_string(filename)
    check.check_string(key)
    table_name = self._table_name(filename)
    self._call_sqlite('set_value', self._set_value_i, table_name, key, value)

  def get_value(self, filename, key):
    check.check_string(filename)
    check.check_string(key)
    table_name = self._table_name(filename)
    if not self._db.has_table(table_name):
      return None
    sql = 'select value from {table_name} where key={key}'.format(table_name = table_name,
                                                                  key = string_util.quote(key))
    result = self._db.select_one(sql)
    if result is None:
      return None
    return result[0]

  def clear(self, filename):
    check.check_string(filename)
    table_name = self._table_name(filename)
    self._call_sqlite('clear', self._clear_i, table_name)

  def _call_sqlite(self, label, function, *args):
    try:
      self._db.begin()
      function(*args)
      self._db.commit()
    except Exception as ex:
      try:
        self._db.rollback()
      except Exception as sqlite_ex:
        print('%s: CAUGHT EXCEPTION ROLLING BACK: %s' % (label, str(sqlite_ex)))
      raise ex
    
  def _ensure_table_(self, table_name):
    'Ensure that a table exists.  Does not commit.'
    if self._db.has_table(table_name):
      return
    schema = self._METADATA_SCHEMA.format(table_name = table_name)
    self._db.execute(schema)
    
  def _replace_values_i(self, table_name, values):
    'Do the replace_values work without transactions.'
    if not values and not self._db.has_table(table_name):
      return
    if not values:
      sql = 'delete from {table_name}'.format(table_name = table_name)
      self._db.execute(sql)
      return
    self._ensure_table_(table_name)
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
    self._ensure_table_(table_name)
    sql = 'insert or replace into {table_name} (key, value) values (?, ?)'.format(table_name = table_name)
    self._db.execute(sql, ( key, value ))
    
  @classmethod
  def _quoted_keys(clazz, kvl):
    return [ string_util.quote(key) for key in kvl.all_keys() ]
  
