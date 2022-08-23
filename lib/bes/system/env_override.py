#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path
import tempfile
import copy
from functools import wraps

from .check import check
from .env_override_options import env_override_options
from .env_var import env_var
from .filesystem import filesystem
from .environment import environment
from .host import host
from .os_env import os_env

class env_override(object):

  def __init__(self, env = None, options = None):
    check.check_dict(env, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)
    check.check_env_override_options(options, allow_none = True)

    if env and options:
      raise ValueError(f'Only one of "env" or "options" should be given.')
    options = options or env_override_options()
    options.verify()

    if env:
      options.env_add = copy.deepcopy(env)
    
    self._options = options
    self._original_env = None
    self._delete_tmp_dirs = []
    
    self._stack = []

  def _resolve_env(self):
    env = self._resolve_base_env(self._options)
    env_add = self._options.env_add or {}
    PATH = self._options.resolve_PATH(env)
    if PATH != None:
      env.update({ 'PATH': PATH })
    PYTHONPATH = self._options.resolve_PYTHONPATH(env)
    if PYTHONPATH != None:
      env.update({ 'PYTHONPATH': PYTHONPATH })
    env_keys = set([ key for key in env.keys() ])
    env_add_keys = set([ key for key in env_add.keys() ])
    intersection = env_keys.intersection(env_add_keys)
    clobber_ignore_keys = self._options.clobber_ignore_keys()
    allow_override_keys = set(self._options.allow_override_keys or [])
    intersection = intersection - clobber_ignore_keys - allow_override_keys
    #for key in clobber_ignore_keys:
    #  if key in intersection:
    #    intersection.remove(x)
    #assert intersection == poto
    if intersection:
      raise RuntimeError(f'the base env and env_add have clashing keys: {" ".join(intersection)}')
    env.update(env_add)
    return env
    
  def __enter__(self):
    self._original_env = os_env.clone_current_env()
    env = self._resolve_env()
    
    home_dir = self._options.resolve_home_dir()
    if home_dir:
      home_dir_env = environment.home_dir_env(home_dir.where)
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
    os_env.set_current_env(self._original_env)
    for next_dir in self._delete_tmp_dirs:
      filesystem.remove_directory(next_dir)
    
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

    options = env_override_options(enter_functions = enter_functions,
                                   exit_functions = exit_functions,
                                   home_dir_use_temp = not use_temp_home,
                                   home_dir = use_temp_home,
                                   env_add = extra_env)
    return env_override(options = options)

  @classmethod
  def temp_tmpdir(clazz):
    'Return an env_override object with a temporary TMPDIR'
    options = env_override_options(tmp_dir_use_temp = True)
    return env_override(options = options)

  @classmethod
  def clean_env(clazz):
    'Return a clean env useful for testing where a deterministic clean environment is needed.'
    options = env_override_options(clean_env = True)
    return env_override(options = options)

  @classmethod
  def path_append(clazz, p):
    'Return an env_override object with p appended to PATH'
    options = env_override_options(path_append = p)
    return env_override(options = options)

  @classmethod
  def tmpdir_files(clazz):
    tmpdir = tempfile.gettempdir()
    files = os.listdir(tmpdir)
    return sorted([ path.join(tmpdir, f) for f in files ])

  @classmethod
  def _resolve_base_env(clazz, options):
    if options.clean_env:
      result = os_env.make_clean_env()
    elif options.env:
      result = copy.deepcopy(options.env)
    else:
      result = os_env.clone_current_env()
    return result
  
def env_override_temp_home_func():
  'A decarator to override HOME for a function.'
  def _wrap(func):
    @wraps(func)
    def _caller(self, *args, **kwargs):
      with env_override.temp_home() as env:
        return func(self, *args, **kwargs)
    return _caller
  return _wrap
