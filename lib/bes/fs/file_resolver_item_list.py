#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.common.type_checked_list import type_checked_list

from .file_resolver_item import file_resolver_item

class file_resolver_item_list(type_checked_list):

  __value_type__ = file_resolver_item
  
  def __init__(self, values = None):
    super(file_resolver_item_list, self).__init__(values = values)

  def absolute_files(self, sort = False):
    result = [ item.filename_abs for item in self ]
    if sort:
      result = sorted(result)
    return result

  def relative_files(self, sort = False):
    result = [ item.filename for item in self ]
    if sort:
      result = sorted(result)
    return result
  
check.register_class(file_resolver_item_list, include_seq = False)
