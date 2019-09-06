#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.compat.StringIO import StringIO
from bes.common.check import check
from bes.common.type_checked_list import type_checked_list

from .vfs_file_info import vfs_file_info

class vfs_file_info_list(type_checked_list):

  __value_type__ = vfs_file_info
  
  def __init__(self, values = None):
    super(vfs_file_info_list, self).__init__(values = values)

  def to_string(self, delimiter = '\n'):
    buf = StringIO()
    first = True
    for vfs_file_info in iter(self):
      if not first:
        buf.write(delimiter)
      first = False
      buf.write(str(vfs_file_info))
    return buf.getvalue()
  
  def __str__(self):
    return self.to_string()
  
check.register_class(vfs_file_info_list, include_seq = False)
