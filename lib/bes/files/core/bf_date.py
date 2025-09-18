#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path
from datetime import datetime
from datetime import timedelta

from bes.system.check import check

from .bf_check import bf_check

class bf_date(object):

  @classmethod
  def get_modification_date(clazz, filename):
    filename = bf_check.check_file_or_dir(filename)
    
    ts = path.getmtime(filename)
    return datetime.fromtimestamp(ts)

  @classmethod
  def set_modification_date(clazz, filename, mtime):
    filename = bf_check.check_file_or_dir(filename)
    check.check_datetime(mtime)

    ts = mtime.timestamp()
    os.utime(filename, ( ts, ts ))

  @classmethod
  def touch(clazz, filename):
    'Update the modification date of filename to be now'
    clazz.set_modification_date(filename, datetime.now())
    
