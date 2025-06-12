# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from collections import namedtuple

from ..system.check import check
from bes.common.string_util import string_util
from bes.property.cached_property import cached_property
from bes.common.type_checked_list import type_checked_list
from bes.common.json_util import json_util

class bat_vmware_shared_folder(namedtuple('bat_vmware_shared_folder', 'folder_id, host_path, host_path_abs, flags')):
  'A class to represent a vmware vm shared folder.'
  
  def __new__(clazz, folder_id, host_path, flags):
    check.check_string(folder_id)
    check.check_string(host_path)
    check.check_int(flags)

    host_path_abs = path.abspath(path.expanduser(host_path))
    return clazz.__bases__[0].__new__(clazz, folder_id, host_path, host_path_abs, flags)

  @cached_property
  def host_path_abs(self):
    return path.abspath(path.expanduser(self.host_path))

  def to_dict(self):
    return {
      'folder_id': self.folder_id,
      'host_path': self.host_path,
      'flags': self.flags,
    }

  def to_json(self):
    return json_util.to_json(self.to_dict(), indent = 2, sort_keys = True)
  
check.register_class(bat_vmware_shared_folder, include_seq = False)

class bat_vmware_shared_folder_list(type_checked_list):

  __value_type__ = bat_vmware_shared_folder
  
  def __init__(self, values = None):
    super(bat_vmware_shared_folder_list, self).__init__(values = values)

  def to_list(self):
    return [ f.to_dict() for f in self ]

  def to_json(self):
    l = self.to_list()
    return json_util.to_json(l, indent = 2, sort_keys = True)

  def has_folder_id(self, folder_id):
    for f in self:
      if f.folder_id == folder_id:
        return True
    return False
  
check.register_class(bat_vmware_shared_folder_list, include_seq = False)
  
