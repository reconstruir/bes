#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_enum import checked_enum

class bf_media_finder_state(checked_enum):
  IDLE        = 'idle'
  SCANNING    = 'scanning'
  READY_QUICK = 'ready_quick'
  RESOLVING   = 'resolving'
  READY       = 'ready'

bf_media_finder_state.register_check_class()
