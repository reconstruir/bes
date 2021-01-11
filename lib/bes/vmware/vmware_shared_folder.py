# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from collections import namedtuple

from bes.common.check import check
from bes.common.string_util import string_util
from bes.property.cached_property import cached_property

class vmware_shared_folder(namedtuple('vmware_shared_folder', 'folder_id, host_path, host_path_abs, flags')):
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
