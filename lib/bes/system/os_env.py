#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import os.path as path
import os

from .host import host
from .env_var import os_env_var
from .environment import environment

class os_env(object):

  DEFAULT_SYSTEM_PATH = environment.default_path()
    
  # Map of system to the runtime loader path
  LOADER_PATH_MAP = {
    host.LINUX: 'LD_LIBRARY_PATH',
    host.MACOS: 'DYLD_LIBRARY_PATH',
    host.WINDOWS: None,
  }

  POSSIBLE_LD_LIBRARY_PATH_VAR_NAMES = [ 'LD_LIBRARY_PATH', 'DYLD_LIBRARY_PATH' ]

  LD_LIBRARY_PATH_VAR_NAME = LOADER_PATH_MAP[host.SYSTEM]

  PATH = os_env_var('PATH')

  # variables to keep in a clean environment when wiping it to have deterministic results
  CLEAN_ENV_VARS = environment.clean_variables()

  # keys for env vars that can be interpreted as paths ala PATH or PYTHONPATH
  KEYS_THAT_ARE_PATHS = set([
    'CLASSPATH',
    'DYLD_LIBRARY_PATH',
    'LD_LIBRARY_PATH',
    'MANPATH',
    'PATH',
    'PERL5LIB',
    'PERL_LIB',
    'PKG_CONFIG_PATH',
    'PYTHONPATH',
   ])

  @classmethod
  def make_clean_env(clazz, keep_keys = None, update = None, prepend = True,
                     keep_func = None, allow_override = False):
    'Return a clean environment suitable for deterministic build related tasks.'
    keep_keys = keep_keys or []
    env = { k: v for k,v in os.environ.items() if k in clazz.CLEAN_ENV_VARS }
    env['PATH'] = os.pathsep.join(environment.clean_path())
    for key in keep_keys:
      if key in os.environ:
        env[key] = os.environ[key]
    if keep_func:
      for key, value in os.environ.items():
        if keep_func(key):
          env[key] = value
    if update:
      assert isinstance(update, dict)
      clazz.update(env, update, prepend = prepend, allow_override = allow_override)
    return env

  @classmethod
  def make_shell_env(clazz, root_dir):
    env = {
      clazz.LD_LIBRARY_PATH_VAR_NAME: path.join(root_dir, 'lib'),
      'PATH': path.join(root_dir, 'bin'),
      'PYTHONPATH': path.join(root_dir, 'lib/python'),
    }
    return env
  
  @classmethod
  def path_reset(clazz):
    'Reset PATH to a very basic list of system specific defaults.'
    os_env_var('PATH').value = environment.clean_path()

  @classmethod
  def update(clazz, env, d, prepend = True, allow_override = False):
    'Update env with d taking into account paths that needed to be appended.'
    d = d or {}
    for key, value in d.items():
      if clazz.key_is_path(key):
        clazz._env_path_update(env, d, key, prepend = prepend)
      else:
        # Dont allow silent override of an existing key if the value changes
        if not allow_override:
          if key in env and env[key] != d[key]:
            raise RuntimeError('Trying to change %s from \"%s\" to \"%s\"' % (key, env[key], d[key]))
        env[key] = d[key]
        
  @classmethod
  def clone_and_update(clazz, env, d, prepend = False, allow_override = False):
    'Clone and update env with d taking into account paths that needed to be appended.'
    env = copy.deepcopy(env)
    clazz.update(env, d, prepend = prepend, allow_override = allow_override)
    return env

  @classmethod
  def clone_current_env(clazz, d = None, prepend = False, allow_override = False):
    'Clone the current environment and update it with d taking into account paths that needed to be appended or prepended.'
    return clazz.clone_and_update(dict(os.environ),
                                  d = d,
                                  prepend = prepend,
                                  allow_override = allow_override)
    
  @classmethod
  def set_current_env(clazz, d):
    assert isinstance(d, dict)
    os.environ.clear()
    os.environ.update(copy.deepcopy(d))
  
  @classmethod
  def _env_path_update(clazz, env, d, key, prepend = False):
    current_value = os_env_var.path_split(env.get(key, ''))
    additional_value = os_env_var.path_split(d[key])
    if prepend:
      new_value = additional_value + current_value
    else:
      new_value = current_value + additional_value
    env[key] = os_env_var.path_join(os_env_var.path_cleanup(new_value))
    
  @classmethod
  def key_is_path(clazz, key):
    'Return True if the given key is a list.'
    return key in clazz.KEYS_THAT_ARE_PATHS
