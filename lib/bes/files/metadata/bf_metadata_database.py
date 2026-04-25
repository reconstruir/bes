#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import threading
import time

from bes.sqlite.sqlite import sqlite
from bes.system.check import check
from bes.system.log import logger

class bf_metadata_database:

  _log = logger('bf_metadata_database')

  SCHEMA_VERSION = 1
  _VACUUM_ROW_THRESHOLD = 50_000
  _VACUUM_AGE_DAYS = 180

  _METADATA_V1_SCHEMA = r'''
create table metadata_v1 (
  checksum   text    not null,
  key        text    not null,
  value      text    not null,
  stored_at  integer not null,
  primary key (checksum, key)
)
'''

  _IDX_CHECKSUM_SCHEMA = r'''
create index idx_checksum on metadata_v1(checksum)
'''

  _IDX_STORED_AT_SCHEMA = r'''
create index idx_stored_at on metadata_v1(stored_at)
'''

  def __init__(self, database_path):
    check.check_string(database_path)

    self._database_path = database_path
    self._lock = threading.Lock()
    self._db = sqlite(database_path, check_same_thread = False)
    self._db.execute('PRAGMA journal_mode=WAL')
    self._setup_schema()
    self._vacuum_if_needed()

  def _setup_schema(self):
    if not self._db.has_table('metadata_v1'):
      self._create_data_tables()
      return
    stored_version = self._db.get_table_version('metadata_v1')
    if stored_version == self.SCHEMA_VERSION:
      return
    self._db.execute('DROP TABLE IF EXISTS metadata_v1')
    self._db.execute('DROP INDEX IF EXISTS idx_checksum')
    self._db.execute('DROP INDEX IF EXISTS idx_stored_at')
    self._create_data_tables()

  def _create_data_tables(self):
    self._db.ensure_table('metadata_v1', self._METADATA_V1_SCHEMA)
    self._db.ensure_index('idx_checksum', self._IDX_CHECKSUM_SCHEMA)
    self._db.ensure_index('idx_stored_at', self._IDX_STORED_AT_SCHEMA)
    self._db.set_table_version('metadata_v1', self.SCHEMA_VERSION)
    self._db.commit()

  def schema_version(self):
    with self._lock:
      return self._db.get_table_version('metadata_v1')

  def get(self, checksum, key):
    check.check_string(checksum)
    check.check_string(key)

    with self._lock:
      row = self._db.select_one(
        'select value from metadata_v1 where checksum = ? and key = ?',
        (checksum, key)
      )
      return row[0] if row else None

  def set(self, checksum, key, value):
    check.check_string(checksum)
    check.check_string(key)
    check.check_string(value)

    self._log.log_method_d()
    
    with self._lock:
      self._db.execute(
        'insert or replace into metadata_v1 values (?, ?, ?, ?)',
        (checksum, key, value, int(time.time()))
      )
      self._db.commit()

  def delete(self, checksum, key = None):
    check.check_string(checksum)
    check.check_string(key, allow_none = True)

    with self._lock:
      if key is None:
        self._db.execute(
          'delete from metadata_v1 where checksum = ?',
          (checksum,)
        )
      else:
        self._db.execute(
          'delete from metadata_v1 where checksum = ? and key = ?',
          (checksum, key)
        )
      self._db.commit()

  def keys(self, checksum):
    check.check_string(checksum)

    with self._lock:
      rows = self._db.select_all(
        'select key from metadata_v1 where checksum = ? order by key asc',
        (checksum,)
      )
      return [ row[0] for row in rows ]

  def get_all(self, checksum):
    check.check_string(checksum)

    with self._lock:
      rows = self._db.select_all(
        'select key, value from metadata_v1 where checksum = ? order by key asc',
        (checksum,)
      )
      return { row[0]: row[1] for row in rows }

  def row_count(self):
    with self._lock:
      row = self._db.select_one('select count(*) from metadata_v1')
      return row[0]

  def _vacuum_if_needed(self):
    with self._lock:
      row = self._db.select_one('select count(*) from metadata_v1')
      if row[0] < self._VACUUM_ROW_THRESHOLD:
        return
      cutoff = int(time.time()) - self._VACUUM_AGE_DAYS * 86400
      row = self._db.select_one(
        'select count(*) from metadata_v1 where stored_at < ?',
        (cutoff,)
      )
      if row[0] == 0:
        return
      self._db.execute('delete from metadata_v1 where stored_at < ?', (cutoff,))
      self._db.commit()

  def close(self):
    self._db._connection.close()
