#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path
import pprint

from bes.common.check import check
from bes.fs.file_util import file_util
from bes.fs.file_path import file_path
from bes.system.os_env import os_env
from bes.system.which import which
from bes.system.command_line import command_line
from bes.system.execute import execute
from bes.system.log import logger
from bes.system.env_override import env_override

from .pyinstaller_error import pyinstaller_error

from PyInstaller.__main__ import run as PyInstaller_run

class pyinstaller_exe(object):
  'Class to deal with the pyinstaller executable.'

  _log = logger('pyinstaller')
  
  @classmethod
  def call_pyinstaller(clazz, args, build_dir = None, replace_env = None):
    check.check_string_seq(args)
    check.check_string(build_dir, allow_none = True)
    check.check_dict(replace_env, check.STRING_TYPES, check.STRING_TYPES)
    
    cmd = command_line.parse_args(args)
    replace_env = replace_env or {}
    env = os_env.clone_current_env(d = {})
    env.update(replace_env)
    clazz._log.log_d('using env: {}'.format(pprint.pformat(env)))
    clazz._log.log_d('calling pyinstaller: {}'.format(' '.join(cmd)))
    if build_dir:
      file_util.mkdir(build_dir)
    dist_dir = path.join(build_dir, 'dist')
    work_dir = path.join(build_dir, 'work')
    args = args[:]
    args.extend([ '--distpath', dist_dir ])
    try:
      with env_override(env = env) as _:
        PyInstaller_run(pyi_args = args, pyi_config = None)
    except Exception as ex:
      print('caught: {}'.format(str(ex)))
      raise
    #raise pyinstaller_error(str(ex))
 
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
