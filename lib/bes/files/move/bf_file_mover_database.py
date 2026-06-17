#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import threading

from bes.sqlite.sqlite import sqlite
from bes.system.check import check

from .bf_file_mover_operation import bf_file_mover_operation
from .bf_file_mover_status import bf_file_mover_status

class bf_file_mover_database:

  SCHEMA_VERSION = 1

  _OPERATIONS_SCHEMA = r'''
create table move_operations_v1 (
  operation_id          text    primary key not null,
  source_path           text    not null,
  staging_path          text    not null,
  destination_path      text    not null,
  destination_device_id text,
  status                text    not null,
  submitted_at          integer not null,
  staged_at             integer,
  copy_started_at       integer,
  paused_at             integer,
  completed_at          integer,
  error_message         text
)
'''

  _IDX_STATUS_SCHEMA = r'''
create index idx_move_status on move_operations_v1(status)
'''

  _IDX_SUBMITTED_AT_SCHEMA = r'''
create index idx_move_submitted_at on move_operations_v1(submitted_at)
'''

  def __init__(self, database_path):
    check.check_string(database_path)

    self._database_path = database_path
    self._lock = threading.Lock()
    self._db = sqlite(database_path, check_same_thread=False)
    self._db.execute('PRAGMA journal_mode=WAL')
    self._setup_schema()

  def _setup_schema(self):
    if not self._db.has_table('move_operations_v1'):
      self._create_tables()
      return
    stored_version = self._db.get_table_version('move_operations_v1')
    if stored_version == self.SCHEMA_VERSION:
      return
    self._db.execute('DROP TABLE IF EXISTS move_operations_v1')
    self._db.execute('DROP INDEX IF EXISTS idx_move_status')
    self._db.execute('DROP INDEX IF EXISTS idx_move_submitted_at')
    self._create_tables()

  def _create_tables(self):
    self._db.ensure_table('move_operations_v1', self._OPERATIONS_SCHEMA)
    self._db.ensure_index('idx_move_status', self._IDX_STATUS_SCHEMA)
    self._db.ensure_index('idx_move_submitted_at', self._IDX_SUBMITTED_AT_SCHEMA)
    self._db.set_table_version('move_operations_v1', self.SCHEMA_VERSION)
    self._db.commit()

  def schema_version(self):
    with self._lock:
      return self._db.get_table_version('move_operations_v1')

  def delete_all_operations(self):
    with self._lock:
      self._db.execute('DELETE FROM move_operations_v1')
      self._db.commit()

  def insert_operation(self, operation):
    with self._lock:
      self._db.execute(
        'INSERT INTO move_operations_v1 VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
        (operation.operation_id,
         operation.source_path,
         operation.staging_path,
         operation.destination_path,
         operation.destination_device_id,
         operation.status.value,
         operation.submitted_at,
         operation.staged_at,
         operation.copy_started_at,
         operation.paused_at,
         operation.completed_at,
         operation.error_message)
      )
      self._db.commit()

  def update_status(self, operation_id, status, **fields):
    check.check_string(operation_id)

    allowed_fields = {'staged_at', 'copy_started_at', 'paused_at', 'completed_at', 'error_message'}
    for key in fields:
      if key not in allowed_fields:
        raise ValueError(f'Unknown field for update: {key!r}')

    set_clauses = ['status = ?']
    values = [status.value]
    for key, value in fields.items():
      set_clauses.append(f'{key} = ?')
      values.append(value)
    values.append(operation_id)

    sql = f'UPDATE move_operations_v1 SET {", ".join(set_clauses)} WHERE operation_id = ?'
    with self._lock:
      self._db.execute(sql, values)
      self._db.commit()

  def get_operation(self, operation_id):
    check.check_string(operation_id)

    with self._lock:
      row = self._db.select_one(
        'SELECT * FROM move_operations_v1 WHERE operation_id = ?',
        (operation_id,)
      )
      return self._row_to_operation(row) if row else None

  def list_operations(self, status=None, since=None, before=None):
    conditions = []
    params = []

    if status is not None:
      conditions.append('status = ?')
      params.append(status.value)
    if since is not None:
      conditions.append('submitted_at >= ?')
      params.append(since)
    if before is not None:
      conditions.append('submitted_at <= ?')
      params.append(before)

    sql = 'SELECT * FROM move_operations_v1'
    if conditions:
      sql += ' WHERE ' + ' AND '.join(conditions)
    sql += ' ORDER BY submitted_at ASC'

    with self._lock:
      rows = self._db.select_all(sql, params)
      return [self._row_to_operation(row) for row in rows]

  def _row_to_operation(self, row):
    return bf_file_mover_operation(
      operation_id=row[0],
      source_path=row[1],
      staging_path=row[2],
      destination_path=row[3],
      destination_device_id=row[4],
      status=bf_file_mover_status(row[5]),
      submitted_at=row[6],
      staged_at=row[7],
      copy_started_at=row[8],
      paused_at=row[9],
      completed_at=row[10],
      error_message=row[11],
    )
