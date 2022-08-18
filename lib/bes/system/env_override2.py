#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path
import tempfile
import copy
from functools import wraps

from ..system.check import check
from .env_var import env_var
from .filesystem import filesystem
from .host import host
from .os_env import os_env

from .env_override_options import env_override_options

class env_override2(object):

  def __init__(self, options = None):
    check.check_env_override_options(options, allow_none = True)

    options = options or env_override_options()
    
    if options.env_override and options.clean_env:
      raise ValueError(f'Only one of "env_override" or "clean_env" should be given.')
    
    self._options = options
    self._original_env = None
    self._delete_tmp_dirs = []
    
    self._stack = []
    #self._env = env

  def _resolve_env(self):
    env = self._options.resolve_base_env()
    env_add = self._options.env_add or {}
    env_keys = set([ key for key in env.keys() ])
    env_add_keys = set([ key for key in env_add.keys() ])
    intersection = env_keys.intersection(env_add_keys)
    if intersection:
      raise RuntimeError(f'the base env and env_add have clashing keys: {" ".join(intersection)}')
    env.update(env_add)
    PATH = self._options.resolve_PATH(env)
    if PATH != None:
      env.update({ 'PATH': PATH.value })
    return env
    
  def __enter__(self):
    self._original_env = os_env.clone_current_env()
    env = self._resolve_env()

    home_dir = self._options.resolve_home_dir()
    if home_dir:
      home_dir_env = filesystem.home_dir_env(home_dir.where)
      if home_dir.delete:
        self._delete_tmp_dirs.append(home_dir.where)
      env.update(home_dir_env)

    tmp_dir = self._options.resolve_tmp_dir()
    if tmp_dir:
      tmp_dir_env = {
        'TMPDIR': tmp_dir,
        'TEMP': tmp_dir,
        'TMP': tmp_dir,
      }
      if tmp_dir.delete:
        self._delete_tmp_dirs.append(tmp_dir.where)
      env.update(tmp_dir_env)
      
    os_env.set_current_env(env)
    
    for func in self._options.enter_functions or []:
      func()
    return self
  
  def __exit__(self, type, value, traceback):
    for func in self._options.exit_functions or []:
      func()

    for next_dir in self._delete_tmp_dirs:
      filesystem.remove_directory(next_dir)
      
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
    return copy.deepcopy(dict(os.environ))

  @classmethod
  def temp_home(clazz, enter_functions = None, exit_functions = None, use_temp_home = None, extra_env = None):
    'Return an env_override object with a temporary HOME'
    check.check_callable_seq(enter_functions, allow_none = True)
    check.check_callable_seq(exit_functions, allow_none = True)

    exit_functions = exit_functions or []
    
    if use_temp_home:
      tmp_home = use_temp_home
    else:
      tmp_home = tempfile.mkdtemp(suffix = '-tmp-home.dir')
      filesystem.atexit_remove(tmp_home)
      # There are some processes that dont call atexit because of
      # being daemons or forker workers in multiprocessing pools or something
      # so we always try to cleanup in the exit handler
      exit_functions.append(lambda: filesystem.remove(tmp_home))

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
    if extra_env:
      for key, value in env.items():
        if key in extra_env:
          raise RuntimeError(f'key is already in env: "{key}"')
      env.update(extra_env)
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
    'Return a clean env useful for testing where a deterministic clean environment is needed.'
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
