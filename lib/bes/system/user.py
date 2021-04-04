#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from .host import host

class user(object):

  if host.is_unix():
    import pwd
    info = pwd.getpwuid(os.getuid())
    USERNAME = info.pw_name
    HOME = info.pw_dir
  elif host.is_windows():
    USERNAME = os.environ.get('USERNAME')
    HOME = os.environ.get('HOME_DIR')
  else:
    host.raise_unsupported_system()
