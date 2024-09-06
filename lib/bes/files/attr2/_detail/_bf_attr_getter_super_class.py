#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.host import host

HAS_XATTR = False
try:
  import xattr
  HAS_XATTR = True
except ModuleNotFoundError as ex:
  pass

#HAS_XATTR = False
#print('HAS_XATTR={}'.format(HAS_XATTR))

if HAS_XATTR:
  from ._bf_attr_getter_xattr import _bf_attr_getter_xattr as _super_class
elif host.SYSTEM == host.MACOS:
  from ._bf_attr_getter_macos_xattr_exe import _bf_attr_getter_macos_xattr_exe as _super_class
elif host.SYSTEM == host.LINUX:
  from ._bf_attr_getter_linux_attr_exe import _bf_attr_getter_linux_attr_exe as _super_class
elif host.SYSTEM == host.WINDOWS:
  from ._bf_attr_getter_windows_ads import _bf_attr_getter_windows_ads as _super_class
else:
  host.raise_unsupported_system()

class _bf_attr_getter_super_class(_super_class):
  pass
