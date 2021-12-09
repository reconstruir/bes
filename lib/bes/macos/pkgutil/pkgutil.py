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

    env = os_env.clone_current_env(d = {})
    rv = pkgutil_command.call_command(args, raise_error = False, env = env, use_sudo = use_sudo)
    if rv.exit_code != 0:
      if not msg:
        cmd_flat = ' '.join(args)
        msg = 'pkgutil command failed: {}\n{}'.format(cmd_flat, rv.stdout)
      raise pkgutil_error(msg)
    return rv
