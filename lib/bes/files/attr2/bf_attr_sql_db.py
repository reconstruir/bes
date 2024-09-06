#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger
from bes.sqlite.sqlite import sqlite

class bf_attr_sql_db(object):

  log = logger('bf_attr_sql')
  
  _FILE_ATTRIBUTES_V1_TABLE_SCHEMA = r'''
CREATE TABLE file_attributes_v1(
  hash_key TEXT NOT NULL,
  attribute_name TEXT NOT NULL,
  attribute_value BLOB,
  PRIMARY KEY (hash_key, attribute_name)
);
'''

  _FILE_ATTRIBUTES_V1_NAME_INDEX_SCHEMA = r'''
CREATE INDEX idx_attribute_name_v1 ON file_attributes_v1(attribute_name);  
'''
  
  def __init__(self, db_filename):
    check.check_string(db_filename)
    
    self._db_filename = db_filename
    self._db = sqlite(self._db_filename)
    self._db.ensure_table('file_attributes_v1', self._FILE_ATTRIBUTES_V1_TABLE_SCHEMA)
    self._db.ensure_index('idx_attribute_name_v1', self._FILE_ATTRIBUTES_V1_NAME_INDEX_SCHEMA)

  def get_bytes(self, hash_key, attribute_name):
    check.check_string(hash_key)
    check.check_string(attribute_name)

    row = self._db.select_one('SELECT attribute_value FROM file_attributes_v1 WHERE hash_key=? AND attribute_name=? ',
                              ( hash_key, attribute_name ))
    return row[0]

  def set_bytes(self, hash_key, attribute_name, attribute_value):
    check.check_string(hash_key)
    check.check_string(attribute_name)
    check.check_bytes(attribute_value)

    self._db.execute('REPLACE INTO file_attributes_v1(hash_key, attribute_name, attribute_value) values(?, ?, ?)',
                     ( hash_key, attribute_name, attribute_value ))

  def has_attribute(self, hash_key, attribute_name):
    check.check_string(hash_key)
    check.check_string(attribute_name)

    row = self._db.select_one('SELECT attribute_name FROM file_attributes_v1 WHERE hash_key=? AND attribute_name=?',
                              ( hash_key, attribute_name ))
    return bool(row)

  def remove(self, hash_key, attribute_name):
    check.check_string(hash_key)
    check.check_string(attribute_name)
    
    self._db.execute('DELETE from file_attributes_v1 WHERE hash_key=? AND attribute_name=?',
                     ( hash_key, attribute_name ))

  def all_attributes(self, hash_key):
    check.check_string(hash_key)

    rows = self._db.select_all('SELECT attribute_name FROM file_attributes_v1 WHERE hash_key=?',
                               ( hash_key, ))
    if not rows:
      return ()
    return tuple([ row[0] for row in rows ])

  def clear(self, hash_key):
    check.check_string(hash_key)

    self._db.execute('DELETE from file_attributes_v1 WHERE hash_key=?',
                            ( hash_key, ))
  
  def dump_to_string(self):
    return self._db.dump_to_string()
