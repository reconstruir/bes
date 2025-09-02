#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path
import pprint

from ..system.check import check
from bes.fs.file_util import file_util
from bes.files.bf_path import bf_path
from bes.system.os_env import os_env
from bes.system.which import which
from bes.system.command_line import command_line
from bes.system.execute import execute
from bes.system.log import logger
from bes.system.env_override import env_override
from bes.system.env_override_options import env_override_options

from .pyinstaller_error import pyinstaller_error

from PyInstaller.__main__ import run as PyInstaller_run
from PyInstaller import __version__ as PyInstaller_version

class pyinstaller_exe(object):
  'Class to deal with the pyinstaller executable.'

  _log = logger('pyinstaller')
  
  @classmethod
  def call_pyinstaller(clazz, args, build_dir = None, replace_env = None):
    check.check_string_seq(args)
    check.check_string(build_dir, allow_none = True)
    check.check_dict(replace_env, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)
    
    cmd = command_line.parse_args(args)
    clazz._log.log_d('replace_env={pprint.pformat(env)}')
    clazz._log.log_d('calling pyinstaller: {" ".join(cmd)}')
    if build_dir:
      file_util.mkdir(build_dir)
    dist_dir = path.join(build_dir, 'dist')
    work_dir = path.join(build_dir, 'work')
    spec_dir = path.join(build_dir, 'spec')
    args = args[:]
    args.extend([ '--distpath', dist_dir ])
    args.extend([ '--workpath', work_dir ])
    args.extend([ '--specpath', spec_dir ])
    options = env_override_options(env = replace_env)
    try:
      with env_override(options = options) as _:
        PyInstaller_run(pyi_args = args, pyi_config = None)
    except Exception as ex:
      raise pyinstaller_error(str(ex))

  @classmethod
  def find_exe(clazz, raise_error = False):
    'Return the pyinstaller executable or None if not found'
    return which.which('pyinstaller', raise_error = raise_error)
    
  @classmethod
  def exe_version(clazz, pyinstaller_exe):
    'Return the pyinstaller executable version'
    check.check_string(pyinstaller_exe)

    return PyInstaller_version
