#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.host import host
from .file_attributes_error import file_attributes_error

if host.SYSTEM == host.WINDOWS:
  from ._detail._file_attributes_windows_ads import _file_attributes_windows_ads as _file_attributes_super_class
else:
  from ._detail._file_attributes_xattr import _file_attributes_xattr as _file_attributes_super_class

class file_attributes(_file_attributes_super_class):
  pass
