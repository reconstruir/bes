#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os, os.path as path, tempfile

from .host import host
from .env_var import os_env_var
from .execute import execute

def _default_system_value(key):
  rv = execute.execute([ 'env', '-i', 'bash', '-c', '"echo ${key}"'.format(key = key) ], raise_error = True, shell = False)
  return rv.stdout.strip()

class os_env(object):

  if host.SYSTEM in [ host.LINUX, host.MACOS ]:
    DEFAULT_SYSTEM_PATH = _default_system_value('PATH')
  else:
    DEFAULT_SYSTEM_PATH = [
      r'C:\WINDOWS\system32',
      r'C:\WINDOWS',
      r'C:\WINDOWS\System32\Wbem',
    ]
    
  # The cleanest possible unix PATH
  CLEAN_PATH_MAP = {
    host.LINUX: [ '/usr/local/bin', '/usr/bin', '/bin', '/usr/sbin', '/sbin' ],
    host.MACOS: [ '/usr/local/bin', '/usr/bin', '/bin', '/usr/sbin', '/sbin' ],
    host.WINDOWS: DEFAULT_SYSTEM_PATH,
  }

  # Map of system to the runtime loader path
  LOADER_PATH_MAP = {
    host.LINUX: 'LD_LIBRARY_PATH',
    host.MACOS: 'DYLD_LIBRARY_PATH',
    host.WINDOWS: None,
  }

  POSSIBLE_LD_LIBRARY_PATH_VAR_NAMES = [ 'LD_LIBRARY_PATH', 'DYLD_LIBRARY_PATH' ]

  LD_LIBRARY_PATH_VAR_NAME = LOADER_PATH_MAP[host.SYSTEM]

  _CLEAN_PATH = CLEAN_PATH_MAP[host.SYSTEM]
  
  PATH = os_env_var('PATH')

  # variables to keep in a clean environment when wiping it to have deterministic results
  # FIXME: This list might have to be system specific.
  # FIXME: also i guessed these are important not sure what the real list is
  if host.is_unix():
    CLEAN_ENV_VARS = [
      'DISPLAY',
      'HOME',
      'LANG',
      'SHELL',
      'TERM',
      'TERM_PROGRAM',
      'TMOUT',
      'TMPDIR',
      'USER',
      'XAUTHORITY',
      '__CF_USER_TEXT_ENCODING',
    ]
  elif host.is_windows():
    CLEAN_ENV_VARS = [
      'ALLUSERSPROFILE',
      'APPDATA',
      'COMPUTERNAME',
      'COMSPEC',
      'DRIVERDATA',
      'HOME',
      'HOMEDRIVE',
      'HOMEPATH',
      'LOCALAPPDATA',
      'LOGONSERVER',
      'NUMBER_OF_PROCESSORS',
      'OS',
      'PATH',
      'PATHEXT',
      'PROCESSOR_ARCHITECTURE',
      'PROCESSOR_IDENTIFIER',
      'PROCESSOR_LEVEL',
      'PROCESSOR_REVISION',
      'SESSIONNAME',
      'SYSTEMDRIVE',
      'SYSTEMROOT',
      'TEMP',
      'TMP',
      'USERNAME',
      'USERPROFILE',
      'WINDIR',
    ]

  # variables to keep in a clean environment when wiping it to have deterministic results
  # FIXME: This list might have to be system specific.
  # FIXME: also i guessed these are important not sure what the real list is
  KEYS_THAT_ARE_PATHS = [
    'CLASSPATH',
    'DYLD_LIBRARY_PATH',
    'LD_LIBRARY_PATH',
    'MANPATH',
    'PATH',
    'PERL5LIB',
    'PERL_LIB',
    'PKG_CONFIG_PATH',
    'PYTHONPATH',
   ]

  @classmethod
  def make_clean_env(clazz, keep_keys = None, update = None, prepend = True,
                     keep_func = None, allow_override = False):
    'Return a clean environment suitable for deterministic build related tasks.'
    keep_keys = keep_keys or []
    env = { k: v for k,v in os.environ.items() if k in clazz.CLEAN_ENV_VARS }
    env['PATH'] = os.pathsep.join(clazz._CLEAN_PATH)
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
    value = clazz.CLEAN_PATH_MAP.get(host.SYSTEM, None)
    if value is None:
      raise RuntimeError('Unknown system %s' % (host.SYSTEM))
    os_env_var('PATH').path = value

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
  def clone_current_env(clazz, d = None, prepend = False):
    'Clone the current environment and update it with d taking into account paths that needed to be appended or prepended.'
    return clazz.clone_and_update(dict(os.environ), d = d, prepend = prepend)
    
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

  @classmethod
  def call_python_script(clazz, cmd):
    fallback_python_path = path.normpath(path.join(path.dirname(__file__), '../../..'))
    env = clazz.make_clean_env(keep_keys = [ 'PYTHONPATH' ])
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['PYTHONPATH'] = env['PYTHONPATH'] + ':' + fallback_python_path
    return execute.execute(cmd, env = env, raise_error = False, stderr_to_stdout = True)

  @classmethod
  def default_system_value(clazz, key):
    return _default_system_value(key)
