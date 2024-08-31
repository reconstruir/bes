#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
from bes.system.check import check
#from bes.common.string_util import string_util
#from bes.key_value.key_value import key_value
#from bes.key_value.key_value_list import key_value_list
from bes.system.log import logger
#from bes.system.execute import execute
from bes.sqlite.sqlite import sqlite

class bf_attr_sql_db(object):

  log = logger('bf_attr_sql')
  
  _FILE_ATTRIBUTES_V1_TABLE_SCHEMA = r'''
create table file_attributes_v1(
  hash_key TEXT PRIMARY KEY NOT NULL,
  attribute_name TEXT NOT NULL,
  attribute_value BLOB
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

  def get_value(self, hash_key, attribute_name):
    check.check_string(hash_key)
    check.check_string(attribute_name)

    row = self._db.select_one('SELECT attribute_value FROM file_attributes_v1 WHERE hash_key=? AND attribute_name=? ',
                              ( hash_key, attribute_name ))
    return row[0]

  def set_value(self, hash_key, attribute_name, attribute_value):
    check.check_string(hash_key)
    check.check_string(attribute_name)
    check.check_bytes(attribute_value)

    self._db.execute('REPLACE INTO file_attributes_v1(hash_key, attribute_name, attribute_value) values(?, ?, ?)',
                     ( hash_key, attribute_name, attribute_value ))

  def has_attribute(self, hash_key, attribute_name):
    check.check_string(hash_key)
    check.check_string(attribute_name)

    row = self._db.execute('SELECT COUNT(*) FROM file_attributes_v1 where hash_key=? AND attribute_name=?',
                           ( hash_key, attribute_name ))
    return bool(row)
