#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.system.os_env import os_env
from bes.system.which import which
from bes.system.execute import execute

from .pkgutil_error import pkgutil_error
from .pkgutil_command import pkgutil_command

class pkgutil(object):
  'Class to deal with the pkgutil executable.'
  
  @classmethod
  def call_pkgutil(clazz, args, msg = None, use_sudo = False):
    check.check_string_seq(args)
    check.check_string(msg, allow_none = True)
    check.check_bool(use_sudo)

    cmd = pkgutil_command()
    env = os_env.clone_current_env(d = {})
    rv = cmd.call_command(args, raise_error = False, env = env, use_sudo = use_sudo)
    if rv.exit_code != 0:
      if not msg:
        cmd_flag = ' '.join(cmd)
        msg = 'pkgutil command failed: {}\n{}'.format(cmd_flag, rv.stdout)
      raise pkgutil_error(msg)
    return rv
