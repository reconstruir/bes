#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from .host import host

class user(object):

  if host.is_unix():
    import pwd
    USERNAME = pwd.getpwuid(os.getuid()).pw_name
  elif host.is_windows():
    USERNAME = os.environ.get('USERNAME')
  else:
    host.raise_unsupported_system()
