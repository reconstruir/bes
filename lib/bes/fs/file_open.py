#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from ..common.string_util import string_util
from ..system.check import check
from ..system.execute import execute
from ..system.host import host

class file_open(object):

  @classmethod
  def open_with_system(clazz, *args, wait_for_exit = False):
    'Open a file with the system viewer.'
    check.check_string_seq(args)
    check.check_bool(wait_for_exit)
    check.check_string_seq(args)
    
    quoted_args = [ string_util.quote_if_needed(arg) for arg in args ]
    if host.is_unix():
      os_flags = []
      if host.is_macos():
        open_exe = 'open'
        if wait_for_exit:
          os_flags.append('-W')
      else:
        open_exe = 'xdg-open'
      cmd = [ open_exe ] + os_flags + quoted_args
      execute.execute(cmd)
    elif host.is_windows():
      for quoted_arg in quoted_args:
        os.startfile(quoted_arg)
    else:
      host.raise_unsupported_system()
