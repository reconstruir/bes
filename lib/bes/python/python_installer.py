#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.system.host import host

if host.SYSTEM == 'macos':
  from .python_installer_macos import python_installer_macos as python_installer
elif host.SYSTEM == 'linux':
  from .python_installer_linux import python_installer_linux as python_installer
else:
  host.raise_unsupported_system()

check.register_class(python_installer, name = 'python_installer', include_seq = False)
