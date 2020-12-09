#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint

from bes.common.check import check
from bes.fs.file_util import file_util
from bes.system.os_env import os_env
from bes.system.which import which
from bes.system.command_line import command_line
from bes.system.execute import execute
from bes.system.log import logger

from .pyinstaller_error import pyinstaller_error

class pyinstaller_exe(object):
  'Class to deal with the pyinstaller executable.'

  _log = logger('pyinstaller')
  
  @classmethod
  def call_pyinstaller(clazz, args, cwd = None, replace_env = None, non_blocking = False):
    exe = clazz.find_exe()
    if not exe:
      raise pyinstaller_error('pyinstaller not found')
    cmd = [ exe ] + command_line.parse_args(args)
    replace_env = replace_env or {}
    env = os_env.clone_current_env(d = {})
    env.update(replace_env)
    clazz._log.log_d('using env: {}'.format(pprint.pformat(env)))
    clazz._log.log_d('calling pyinstaller: {}'.format(' '.join(cmd)))
    file_util.mkdir(cwd)
    rv = execute.execute(cmd,
                         env = env,
                         shell = False,
                         cwd = cwd,
                         stderr_to_stdout = True,
                         non_blocking = non_blocking,
                         raise_error = False)
    if rv.exit_code != 0:
      cmd_flag = ' '.join(cmd)
      msg = 'pyinstaller command failed: {}\n{}'.format(cmd_flag, rv.stdout)
      raise pyinstaller_error(msg)
    return rv

  @classmethod
  def find_exe(clazz, raise_error = False):
    'Return the pyinstaller executable or None if not found'
    return which.which('pyinstaller', raise_error = raise_error)

  @classmethod
  def exe_version(clazz, pyinstaller_exe):
    'Return the pyinstaller executable version'
    check.check_string(pyinstaller_exe)
    
    cmd = [ pyinstaller_exe, '--version' ]
    rv = execute.execute(cmd, stderr_to_stdout = True, print_failure = False)
    if rv.exit_code != 0:
      raise pyinstaller_error(str(ex))
    return rv.stdout.strip()
