#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import enum

class bf_file_mover_move_status(enum.Enum):
  success  = 'success'
  no_space = 'no_space'
