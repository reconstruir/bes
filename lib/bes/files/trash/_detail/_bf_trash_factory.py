#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.log import logger
from bes.system.host import host

class _bf_trash_factory(object):

  _log = logger('bf_trash')

  @classmethod
  def get_trash_super_class(clazz):
    if host.is_windows():
      from ._bf_trash_windows import _bf_trash_windows
      return _bf_trash_windows
    elif host.is_linux():
      from ._bf_trash_linux import _bf_trash_linux
      return _bf_trash_linux
    elif host.is_macos():
      from ._bf_trash_macos import _bf_trash_macos
      return _bf_trash_macos
    host.raise_unsupported_system()
