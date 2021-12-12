#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.host import host
from .file_attributes_error import file_attributes_error

_has_xattr=False
try:
  import xattr
  _has_xattr=True
except ImportError as ex:
  pass

#_has_xattr = False

if _has_xattr:
  from ._file_attributes_xattr import _file_attributes_xattr as _file_attributes_super_class
elif host.SYSTEM == host.MACOS:
  from ._file_attributes_macos import _file_attributes_macos as _file_attributes_super_class
elif host.SYSTEM == host.LINUX:
  from ._file_attributes_linux import _file_attributes_linux as _file_attributes_super_class
elif host.SYSTEM == host.WINDOWS:
  from ._file_attributes_windows import _file_attributes_windows as _file_attributes_super_class
else:
  host.raise_unsupported_system()

print('_file_attributes_super_class={}'.format(_file_attributes_super_class))
  
class file_attributes(_file_attributes_super_class):
  pass
