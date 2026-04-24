#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import threading
import time

from bes.sqlite.sqlite import sqlite
from bes.system.check import check
from bes.system.log import logger

class bf_checksum_database:

  _log = logger('bf_checksum_database')

  SCHEMA_VERSION = 1
  _VACUUM_ROW_THRESHOLD = 10_000
  _VACUUM_AGE_DAYS = 90

  _CHECKSUMS_V1_SCHEMA = r'''
create table checksums_v1 (
  fingerprint_key     text not null,
  fingerprint_version integer not null,
  algorithm           text not null,
  checksum            text not null,
  cached_at           integer not null,
  primary key (fingerprint_key, algorithm)
)
'''

  _IDX_FINGERPRINT_VERSION_SCHEMA = r'''
create index idx_fingerprint_version on checksums_v1(fingerprint_version)
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
    if not self._db.has_table('checksums_v1'):
      self._create_data_tables()
      return
    stored_version = self._db.get_table_version('checksums_v1')
    if stored_version == self.SCHEMA_VERSION:
      return
    self._db.execute('DROP TABLE IF EXISTS checksums_v1')
    self._db.execute('DROP INDEX IF EXISTS idx_fingerprint_version')
    self._create_data_tables()

  def _create_data_tables(self):
    self._db.ensure_table('checksums_v1', self._CHECKSUMS_V1_SCHEMA)
    self._db.ensure_index('idx_fingerprint_version', self._IDX_FINGERPRINT_VERSION_SCHEMA)
    self._db.set_table_version('checksums_v1', self.SCHEMA_VERSION)
    self._db.commit()

  def schema_version(self):
    with self._lock:
      return self._db.get_table_version('checksums_v1')

  def get_checksum(self, fingerprint_key, algorithm):
    with self._lock:
      row = self._db.select_one(
        'select checksum from checksums_v1 where fingerprint_key = ? and algorithm = ?',
        (fingerprint_key, algorithm)
      )
      return row[0] if row else None

  def set_checksum(self, fingerprint_key, fingerprint_version, algorithm, checksum):
    with self._lock:
      self._db.execute(
        'insert or replace into checksums_v1 values (?, ?, ?, ?, ?)',
        (fingerprint_key, fingerprint_version, algorithm, checksum, int(time.time()))
      )
      self._db.commit()

  def delete_checksum(self, fingerprint_key, algorithm=None):
    with self._lock:
      if algorithm is None:
        self._db.execute(
          'delete from checksums_v1 where fingerprint_key = ?',
          (fingerprint_key,)
        )
      else:
        self._db.execute(
          'delete from checksums_v1 where fingerprint_key = ? and algorithm = ?',
          (fingerprint_key, algorithm)
        )
      self._db.commit()

  def row_count(self):
    with self._lock:
      row = self._db.select_one('select count(*) from checksums_v1')
      return row[0]

  def _vacuum_if_needed(self):
    with self._lock:
      row = self._db.select_one('select count(*) from checksums_v1')
      if row[0] < self._VACUUM_ROW_THRESHOLD:
        return
      cutoff = int(time.time()) - self._VACUUM_AGE_DAYS * 86400
      row = self._db.select_one(
        'select count(*) from checksums_v1 where cached_at < ?',
        (cutoff,)
      )
      if row[0] == 0:
        return
      self._db.execute('delete from checksums_v1 where cached_at < ?', (cutoff,))
      self._db.commit()

  def close(self):
    self._db._connection.close()
