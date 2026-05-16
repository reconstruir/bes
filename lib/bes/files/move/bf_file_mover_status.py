#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import enum

class bf_file_mover_status(enum.Enum):
  pending      = 'pending'
  staging_done = 'staging_done'
  copying      = 'copying'
  paused       = 'paused'
  done         = 'done'
  failed       = 'failed'
  expired      = 'expired'
  restored     = 'restored'
