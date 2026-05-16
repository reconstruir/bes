#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .bf_file_mover_restore_status import bf_file_mover_restore_status

_DESCRIPTIONS = {
  bf_file_mover_restore_status.success:                  'File restored to its original location.',
  bf_file_mover_restore_status.wrong_status:             'Operation is not in a restorable state (must be failed or paused).',
  bf_file_mover_restore_status.staging_file_missing:     'Staged file no longer exists on disk.',
  bf_file_mover_restore_status.source_directory_missing: 'Original source directory no longer exists.',
  bf_file_mover_restore_status.source_path_occupied:     'A file already exists at the original source path.',
}

class bf_file_mover_restore_result:

  def __init__(self, status, operation_id=None):
    self.status = status
    self.operation_id = operation_id

  @property
  def description(self):
    return _DESCRIPTIONS[self.status]

  def __repr__(self):
    return (
      f'bf_file_mover_restore_result('
      f'status={self.status!r}, '
      f'operation_id={self.operation_id!r})'
    )
