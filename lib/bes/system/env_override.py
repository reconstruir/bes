#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path
import tempfile
import copy
from functools import wraps

from .check import check
from .env_var import env_var
from .filesystem import filesystem
from .host import host
from .os_env import os_env

class env_override(object):

  def __init__(self, env = None, enter_functions = None, exit_functions = None):
    check.check_dict(env, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)
    check.check_function_seq(enter_functions, allow_none = True)
    check.check_function_seq(exit_functions, allow_none = True)

    self._original_env = os_env.clone_current_env()
    self._enter_functions = enter_functions or []
    self._exit_functions = exit_functions or []
    
    self._stack = []
    if env:
      self.update(env)
    
  def __enter__(self):
    for func in self._enter_functions:
      func()
    return self
  
  def __exit__(self, type, value, traceback):
    for func in self._exit_functions:
      func()
    os_env.set_current_env(self._original_env)
    
  def __getitem__(self, key):
    return os.environ.get(key)
    
  def __setitem__(self, key, value):
    os.environ[key] = value
    
  def push(self):
    self._stack.append(os_env.clone_current_env())

  def pop(self):
    d = self._stack.pop()
    os_env.set_current_env(d)

  def set(self, key, value):
    os.environ[key] = value
    
  def get(self, key, default_value = None):
    return os.environ.get(key, default_value)
    
  def update(self, d):
    os.environ.update(d)

  def to_dict(self):
    return copy.deepcopy(os.environ)

  @classmethod
  def temp_home(clazz, enter_functions = None, exit_functions = None):
    'Return an env_override object with a temporary HOME'
    check.check_function_seq(enter_functions, allow_none = True)
    check.check_function_seq(exit_functions, allow_none = True)
    
    tmp_home = tempfile.mkdtemp(suffix = '-tmp-home.dir')
    filesystem.atexit_remove(tmp_home)
    
    if host.is_unix():
      env = { 'HOME': tmp_home }
    elif host.is_windows():
      homedrive, homepath = path.splitdrive(tmp_home)
      env = {
        'HOME': tmp_home,
        'HOMEDRIVE': homedrive,
        'HOMEPATH': homepath,
        'APPDATA': path.join(tmp_home, 'AppData\\Roaming')
      }
    return env_override(env = env,
                        enter_functions = enter_functions,
                        exit_functions = exit_functions)

  @classmethod
  def temp_tmpdir(clazz):
    'Return an env_override object with a temporary TMPDIR'
    tmp_tmpdir = tempfile.mkdtemp(suffix = '-tmp-tmpdir.dir')
    filesystem.atexit_remove(tmp_tmpdir)
    env = {
      'TMPDIR': tmp_tmpdir,
      'TEMP': tmp_tmpdir,
      'TMP': tmp_tmpdir,
    }
    return env_override(env = env)

  @classmethod
  def clean_env(clazz):
    'Return a clean env useful for testing where a determintate clean environment is needed.'
    return env_override(env = os_env.make_clean_env())

  @classmethod
  def path_append(clazz, p):
    'Return an env_override object with p appended to PATH'
    v = env_var(os_env.clone_current_env(), 'PATH')
    v.append(p)
    env = { 'PATH': v.value }
    return env_override(env = env)
  
  @classmethod
  def tmpdir_files(clazz):
    tmpdir = tempfile.gettempdir()
    files = os.listdir(tmpdir)
    return sorted([ path.join(tmpdir, f) for f in files ])

def env_override_temp_home_func():
  'A decarator to override HOME for a function.'
  def _wrap(func):
    @wraps(func)
    def _caller(self, *args, **kwargs):
      with env_override.temp_home() as env:
        return func(self, *args, **kwargs)
    return _caller
  return _wrap
