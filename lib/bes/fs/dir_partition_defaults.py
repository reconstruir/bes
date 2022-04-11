#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

class dir_partition_defaults:

  DELETE_EMPTY_DIRS = False
  DST_DIR = os.getcwd()
  FLATTEN = False
  PARTITION_TYPE = 'prefix'
  THRESHOLD = None
