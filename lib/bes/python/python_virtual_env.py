#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import pprint
import tempfile

from bes.common.check import check

from bes.system.log import logger
from bes.system.execute import execute
from bes.system.os_env import os_env
from bes.system.env_var import env_var
from bes.fs.dir_cleanup import dir_cleanup

from bes.property.cached_property import cached_property

from .python_error import python_error
from .python_exe import python_exe
from .python_installation import python_installation
from .python_source import python_source
from .python_version import python_version

class python_virtual_env(object):
  'Python virtual env thing.'

  _log = logger('python_virtual_env')
  
  def __init__(self, exe, root_dir):
    python_exe.check_exe(exe)
    check.check_string(root_dir)

    self._original_exe = exe
    self._original_version = python_exe.version(self._original_exe)
    if self._original_version < '3.7':
      raise python_error('Python version "{}" not supported.  Minimum supported version is 3.7.'.format(self._original_version))
    self._root_dir = root_dir
    self._call_venv(exe, self._root_dir)
    
  @cached_property
  def python_exe(self):
    original_version = python_exe.version(self._original_exe)
    venv_exe = python_source.virtual_env_python_exe(self._root_dir, original_version)
    if not path.exists(venv_exe):
      raise python_error('venv python exe not found: {}'.format(venv_exe))
    exe_version = python_exe.version(venv_exe)
    if exe_version != original_version:
      raise python_error('version mismatch {} instead of {} for {}'.format(exe_version,
                                                                           original_version,
                                                                           exe))
    return venv_exe

  @cached_property
  def installation(self):
    return python_installation(self.python_exe)
  
  @classmethod
  def _call_venv(clazz, exe, root_dir):
    clazz._log.log_method_d()

    venv_config = path.join(root_dir, 'pyvenv.cfg')
    
    if path.isfile(venv_config):
      return
    
    cmd = [
      exe,
      '-m',
      'venv',
      root_dir,
    ]
    env = os_env.make_clean_env()
    PATH = env_var(env, 'PATH')
    PATH.prepend(path.dirname(exe))
    PYTHONPATH = env_var(env, 'PYTHONPATH')
    PYTHONPATH.unset()
    
    clazz._log.log_d('_call_venv: env={}'.format(pprint.pformat(env)))
    clazz._log.log_d('_call_venv: cmd={}'.format(' '.join(cmd)))

    with dir_cleanup(tempfile.gettempdir()) as ctx:
      rv = execute.execute(cmd, env = env, raise_error = False)
    if rv.exit_code != 0:
      raise python_error('failed to init virtual env: "{}" - {}'.format(' '.join(cmd),
                                                                        rv.stderr))
