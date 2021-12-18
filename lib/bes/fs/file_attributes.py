#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.host import host
from .file_attributes_error import file_attributes_error

HAS_XATTR = False
try:
  import xattr
  HAS_XATTR = True
except ModuleNotFoundError as ex:
  pass

#HAS_XATTR = False
#print('HAS_XATTR={}'.format(HAS_XATTR))

if HAS_XATTR:
  from ._detail._file_attributes_xattr import _file_attributes_xattr as _file_attributes_super_class
elif host.SYSTEM == host.MACOS:
  from ._detail._file_attributes_macos_xattr_exe import _file_attributes_macos_xattr_exe as _file_attributes_super_class
elif host.SYSTEM == host.LINUX:
  from ._detail._file_attributes_linux_attr_exe import _file_attributes_linux_attr_exe as _file_attributes_super_class
elif host.SYSTEM == host.WINDOWS:
  from ._detail._file_attributes_windows import _file_attributes_windows as _file_attributes_super_class
else:
  host.raise_unsupported_system()

class file_attributes(_file_attributes_super_class):
  pass
