#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from bes.system.host import host
if host.is_macos():
  from .native_package_macos import native_package_macos as native_package
elif host.is_linux():
  from .native_package_linux import native_package_linux as native_package
elif host.is_windows():
  from .native_package_windows import native_package_windows as native_package
else:
  host.raise_unsupported_system()

check.register_class(native_package,
                     name = 'native_package',
                     include_seq = False)
