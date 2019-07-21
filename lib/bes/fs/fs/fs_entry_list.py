#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.compat.StringIO import StringIO
from bes.common.check import check
from bes.common.type_checked_list import type_checked_list

from .fs_entry import fs_entry

class fs_entry_list(type_checked_list):

  __value_type__ = fs_entry
  
  def __init__(self, values = None):
    super(fs_entry_list, self).__init__(values = values)

  def to_string(self, delimiter = '\n'):
    buf = StringIO()
    first = True
    for fs_entry in iter(self):
      if not first:
        buf.write(delimiter)
      first = False
      buf.write(str(fs_entry))
    return buf.getvalue()

#  def __hash__(self):
#    return hash(str(self))
  
  def __str__(self):
    return self.to_string()

check.register_class(fs_entry_list, include_seq = False)
