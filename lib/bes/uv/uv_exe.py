#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path
import shutil

from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger

from . import uv_error
from . import uv_exe_info

class uv_exe(object):

  _log = logger('uv_exe')

  @classmethod
  def find(clazz, explicit_path=None):
    'Find the uv binary and return its path. Raises uv_error if not found.'
    candidate = clazz._resolve(explicit_path)
    if not candidate:
      raise uv_error.uv_error(
        'uv binary not found. Install uv or set the UV environment variable.'
      )
    return candidate

  @classmethod
  def find_or_none(clazz, explicit_path=None):
    'Find the uv binary and return its path, or None if not found.'
    return clazz._resolve(explicit_path)

  @classmethod
  def version(clazz, exe_path):
    'Return the version string of the uv binary at exe_path.'
    rv = execute.execute([exe_path, '--version'],
                         raise_error=False,
                         stderr_to_stdout=True,
                         check_python_script=False)
    if rv.exit_code != 0:
      raise uv_error.uv_error(f'Failed to get uv version from {exe_path}: {rv.stdout}')
    parts = rv.stdout.strip().split()
    return parts[1] if len(parts) >= 2 else rv.stdout.strip()

  @classmethod
  def info(clazz, exe_path):
    'Return a uv_exe_info namedtuple for the given binary path.'
    return uv_exe_info.uv_exe_info(exe_path=exe_path, version=clazz.version(exe_path))

  @classmethod
  def _resolve(clazz, explicit_path):
    if explicit_path:
      if path.isfile(explicit_path):
        return explicit_path
      raise uv_error.uv_error(f'Explicit uv exe not found: {explicit_path}')

    uv_env = os.environ.get('UV', None)
    if uv_env and path.isfile(uv_env):
      return uv_env

    local_bin = clazz._local_bin_candidate()
    if local_bin and path.isfile(local_bin):
      return local_bin

    which_result = shutil.which('uv')
    if which_result:
      return which_result

    return None

  @classmethod
  def _local_bin_candidate(clazz):
    if host.is_windows():
      user_profile = os.environ.get('USERPROFILE', path.expanduser('~'))
      return path.join(user_profile, '.local', 'bin', 'uv.exe')
    return path.join(path.expanduser('~'), '.local', 'bin', 'uv')
