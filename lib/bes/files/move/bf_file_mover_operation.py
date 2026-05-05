#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .bf_file_mover_status import bf_file_mover_status

class bf_file_mover_operation:

  def __init__(self,
               operation_id,
               source_path,
               staging_path,
               destination_path,
               destination_device_id,
               status,
               submitted_at,
               staged_at=None,
               copy_started_at=None,
               paused_at=None,
               completed_at=None,
               error_message=None):
    self.operation_id = operation_id
    self.source_path = source_path
    self.staging_path = staging_path
    self.destination_path = destination_path
    self.destination_device_id = destination_device_id
    self.status = status
    self.submitted_at = submitted_at
    self.staged_at = staged_at
    self.copy_started_at = copy_started_at
    self.paused_at = paused_at
    self.completed_at = completed_at
    self.error_message = error_message

  def __repr__(self):
    return (
      f'bf_file_mover_operation('
      f'operation_id={self.operation_id!r}, '
      f'status={self.status!r}, '
      f'source_path={self.source_path!r}, '
      f'destination_path={self.destination_path!r})'
    )
