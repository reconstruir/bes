#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.host import host
from bes.files.bf_check import bf_check

if host.is_windows():
  from ._detail._bf_trash_windows  import _bf_trash_windows
  trash_super_class = _bf_trash_windows
elif host.is_linux():
  from ._detail._bf_trash_linux  import _bf_trash_linux
  trash_super_class = _bf_trash_linux
elif host.is_macos():
  from ._detail._bf_trash_macos  import _bf_trash_macos
  trash_super_class = _bf_trash_macos
else:
  host.raise_unsupported_system()

class bf_trash(trash_super_class):

  pass
