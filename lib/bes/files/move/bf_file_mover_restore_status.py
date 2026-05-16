#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import enum

class bf_file_mover_restore_status(enum.Enum):
  success                  = 'success'
  wrong_status             = 'wrong_status'
  staging_file_missing     = 'staging_file_missing'
  source_directory_missing = 'source_directory_missing'
  source_path_occupied     = 'source_path_occupied'
