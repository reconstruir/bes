#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.host import host

if host.SYSTEM == host.WINDOWS:
  from ._bf_attr_getter_windows_ads import _bf_attr_getter_windows_ads as _super_class
else:
  from ._bf_attr_getter_xattr import _bf_attr_getter_xattr as _super_class

class _bf_attr_getter_super_class(_super_class):
  pass
