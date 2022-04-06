#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..common.time_util import time_util

class dir_combine_defaults:

  DELETE_EMPTY_DIRS = False
  DUP_FILE_COUNT = 1
  DUP_FILE_TIMESTAMP = time_util.timestamp()
  FLATTEN = False
  IGNORE_EMPTY = False
