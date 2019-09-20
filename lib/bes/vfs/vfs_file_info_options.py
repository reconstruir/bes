#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
from bes.common.check import check

class vfs_file_info_options(object):

  def __init__(self, *args, **kargs):
    self.hardcode_modification_date = None
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check(self.hardcode_modification_date, datetime, allow_none = True)
    
  def __str__(self):
    return str(self.__dict__)
    
check.register_class(vfs_file_info_options)
