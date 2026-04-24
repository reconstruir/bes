#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import sqlite3
import threading
import time
from os import path

from bes.system.check import check

class bf_checksum_database:

  SCHEMA_VERSION = 1
  _VACUUM_ROW_THRESHOLD = 10_000
  _VACUUM_AGE_DAYS = 90

  def __init__(self, database_path):
    check.check_string(database_path)

    self._database_path = database_path
    self._lock = threading.Lock()

    if database_path != ':memory:':
      os.makedirs(path.dirname(path.abspath(database_path)), exist_ok=True)

    self._connection = sqlite3.connect(database_path, check_same_thread=False)
    self._connection.execute('PRAGMA journal_mode=WAL')
    self._setup_schema()
    self._vacuum_if_needed()

  def _setup_schema(self):
    with self._lock:
      self._connection.execute('''
        CREATE TABLE IF NOT EXISTS database_metadata (
          key   TEXT PRIMARY KEY NOT NULL,
          value TEXT NOT NULL
        )
      ''')
      self._connection.commit()

      cursor = self._connection.execute(
        "SELECT value FROM database_metadata WHERE key = 'schema_version'"
      )
      row = cursor.fetchone()

      if row is None:
        self._create_data_tables()
        self._connection.execute(
          "INSERT INTO database_metadata VALUES ('schema_version', ?)",
          (str(self.SCHEMA_VERSION),)
        )
        self._connection.commit()
      else:
        stored_version = int(row[0])
        if stored_version != self.SCHEMA_VERSION:
          self._connection.execute('DROP TABLE IF EXISTS checksums_v1')
          self._connection.execute('DROP INDEX IF EXISTS idx_fingerprint_version')
          self._create_data_tables()
          self._connection.execute(
            "UPDATE database_metadata SET value = ? WHERE key = 'schema_version'",
            (str(self.SCHEMA_VERSION),)
          )
          self._connection.commit()

  def _create_data_tables(self):
    self._connection.execute('''
      CREATE TABLE checksums_v1 (
        fingerprint_key     TEXT NOT NULL,
        fingerprint_version INTEGER NOT NULL,
        algorithm           TEXT NOT NULL,
        checksum            TEXT NOT NULL,
        cached_at           INTEGER NOT NULL,
        PRIMARY KEY (fingerprint_key, algorithm)
      )
    ''')
    self._connection.execute(
      'CREATE INDEX idx_fingerprint_version ON checksums_v1(fingerprint_version)'
    )
    self._connection.commit()

  def schema_version(self):
    cursor = self._connection.execute(
      "SELECT value FROM database_metadata WHERE key = 'schema_version'"
    )
    row = cursor.fetchone()
    return int(row[0]) if row else None

  def get_checksum(self, fingerprint_key, algorithm):
    with self._lock:
      cursor = self._connection.execute(
        'SELECT checksum FROM checksums_v1 WHERE fingerprint_key = ? AND algorithm = ?',
        (fingerprint_key, algorithm)
      )
      row = cursor.fetchone()
      return row[0] if row else None

  def set_checksum(self, fingerprint_key, fingerprint_version, algorithm, checksum):
    with self._lock:
      self._connection.execute(
        'INSERT OR REPLACE INTO checksums_v1 VALUES (?, ?, ?, ?, ?)',
        (fingerprint_key, fingerprint_version, algorithm, checksum, int(time.time()))
      )
      self._connection.commit()

  def delete_checksum(self, fingerprint_key, algorithm=None):
    with self._lock:
      if algorithm is None:
        self._connection.execute(
          'DELETE FROM checksums_v1 WHERE fingerprint_key = ?',
          (fingerprint_key,)
        )
      else:
        self._connection.execute(
          'DELETE FROM checksums_v1 WHERE fingerprint_key = ? AND algorithm = ?',
          (fingerprint_key, algorithm)
        )
      self._connection.commit()

  def row_count(self):
    with self._lock:
      cursor = self._connection.execute('SELECT COUNT(*) FROM checksums_v1')
      return cursor.fetchone()[0]

  def _vacuum_if_needed(self):
    with self._lock:
      cursor = self._connection.execute('SELECT COUNT(*) FROM checksums_v1')
      count = cursor.fetchone()[0]
      if count < self._VACUUM_ROW_THRESHOLD:
        return

      cutoff = int(time.time()) - self._VACUUM_AGE_DAYS * 86400
      cursor = self._connection.execute(
        'SELECT COUNT(*) FROM checksums_v1 WHERE cached_at < ?',
        (cutoff,)
      )
      old_count = cursor.fetchone()[0]
      if old_count == 0:
        return

      self._connection.execute(
        'DELETE FROM checksums_v1 WHERE cached_at < ?',
        (cutoff,)
      )
      self._connection.commit()

  def close(self):
    if self._connection:
      self._connection.close()
      self._connection = None
