#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import pprint
import tempfile

from bes.common.check import check
from bes.fs.dir_cleanup import dir_cleanup
from bes.fs.file_symlink import file_symlink
from bes.property.cached_property import cached_property
from bes.system.env_var import env_var
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger
from bes.system.os_env import os_env

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
    self._create(self._root_dir, exe)
    
  @cached_property
  def python_exe(self):
    original_version = python_exe.version(self._original_exe)
    venv_exe = python_source.versioned_python_exe(self._root_dir, original_version)
    if not path.exists(venv_exe):
      raise python_error('venv python exe not found: {}'.format(venv_exe))
    exe_version = python_exe.version(venv_exe)
    if exe_version != original_version:
      raise python_error('version mismatch {} instead of {} for {}'.format(exe_version,
                                                                           original_version,
                                                                           venv_exe))
    return venv_exe

  @cached_property
  def installation(self):
    return python_installation(self.python_exe)
  
  @classmethod
  def _create(clazz, root_dir, exe):
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
    
    clazz._log.log_d('_create: env={}'.format(pprint.pformat(env)))
    clazz._log.log_d('_create: cmd={}'.format(' '.join(cmd)))

    with dir_cleanup(tempfile.gettempdir()) as ctx:
      rv = execute.execute(cmd, env = env, raise_error = False)
    if rv.exit_code != 0:
      raise python_error('failed to init virtual env: "{}" - {}'.format(' '.join(cmd),
                                                                        rv.stderr))
    clazz._ensure_versioned_python_exe(root_dir, exe)
    
  @classmethod
  def _ensure_versioned_python_exe(clazz, root_dir, exe):
    'On some unix systems with certain python versions (3.7) the venv exe with major.minor version is missing.'
    if not host.is_unix():
      return
    version = python_exe.version(exe)
    versioned_exe = python_source.versioned_python_exe(root_dir, version)
    if not path.isfile(versioned_exe):
      exe = python_source.python_exe(root_dir, version)
      file_symlink.symlink(path.basename(exe), versioned_exe)
      if not path.isfile(versioned_exe):
        raise python_error('Failed to create versioned python exe symlink: "{}"'.format(versioned_exe))
