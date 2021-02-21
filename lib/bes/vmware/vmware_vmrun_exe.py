#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.common.string_util import string_util
from bes.system.os_env import os_env
from bes.system.which import which
from bes.system.command_line import command_line
from bes.system.execute import execute
from bes.system.log import logger

from .vmware_error import vmware_error

class vmware_vmrun_exe(object):
  'Class to deal with the vmrun executable.'

  _log = logger('vmware')
  
  @classmethod
  def call_vmrun(clazz, args, extra_env = None, cwd = None,
                 non_blocking = False, shell = False,
                 raise_error = False, error_message = None):
    exe = which.which('vmrun')
    if not exe:
      raise vmware_error('vmrun not found')
    quoted_exe = string_util.quote(exe)
    clazz._log.log_d('call_vmrun: quoted_exe={} args={} - {}'.format(quoted_exe, args, type(args)))
    cmd = [ string_util.quote(exe) ] + command_line.parse_args(args)
    env = os_env.clone_current_env(d = extra_env)
    clazz._log.log_d('call_vmrun: cmd={}'.format(' '.join(cmd)))
    rv = execute.execute(cmd,
                         env = env,
                         shell = shell,
                         cwd = cwd,
                         stderr_to_stdout = True,
                         non_blocking = non_blocking,
                         raise_error = False)
    clazz._log.log_d('call_vmrun: exit_code={}'.format(rv.exit_code))
    if raise_error and rv.exit_code != 0:
      cmd_flat = ' '.join(cmd)
      msg = error_message or 'vmrun command failed: {}\n{}'.format(cmd_flat, rv.stdout)
      raise vmware_error(msg)
    return rv
