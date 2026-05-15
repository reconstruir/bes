#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .bf_file_mover_move_status import bf_file_mover_move_status

_DESCRIPTIONS = {
  bf_file_mover_move_status.success:  'Move operation queued successfully.',
  bf_file_mover_move_status.no_space: 'Destination volume has insufficient free space.',
}

class bf_file_mover_move_result:

  def __init__(self, status, operation_id=None):
    self.status = status
    self.operation_id = operation_id

  @property
  def description(self):
    return _DESCRIPTIONS[self.status]

  def __repr__(self):
    return (
      f'bf_file_mover_move_result('
      f'status={self.status!r}, '
      f'operation_id={self.operation_id!r})'
    )
