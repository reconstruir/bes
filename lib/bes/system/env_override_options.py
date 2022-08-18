#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import copy
import tempfile

from .check import check
from .os_env import os_env

class env_override_options(object):
  
  def __init__(self, *args, **kargs):
    self.clean_env = False
    self.enter_functions = None
    self.exit_functions = None
    self.env_add = None
    self.env_override = None
    self.home_dir = None
    self.home_dir_temp_delete = True
    self.home_dir_temp_prefix = None
    self.home_dir_temp_suffix = None
    self.home_dir_use_temp = False
    self.path_append = None
    self.path_prepend = None
    self.tmp_dir = None
    self.tmp_dir_temp_delete = True
    self.tmp_dir_temp_prefix = None
    self.tmp_dir_temp_suffix = None
    self.tmp_dir_use_temp = False

    for key, value in kargs.items():
      setattr(self, key, value)
      
    check.check_bool(self.clean_env)
    check.check_callable_seq(self.enter_functions, allow_none = True)
    check.check_callable_seq(self.enter_functions, allow_none = True)
    check.check_dict(self.env_add, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)
    check.check_dict(self.env_override, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)
    check.check_string(self.home_dir, allow_none = True)
    check.check_bool(self.home_dir_temp_delete)
    check.check_string(self.home_dir_temp_prefix, allow_none = True)
    check.check_string(self.home_dir_temp_suffix, allow_none = True)
    check.check_bool(self.home_dir_use_temp)
    check.check_string_seq(self.path_append, allow_none = True)
    check.check_string_seq(self.path_prepend, allow_none = True)
    check.check_string(self.tmp_dir, allow_none = True)
    check.check_string(self.tmp_dir_temp_prefix, allow_none = True)
    check.check_string(self.tmp_dir_temp_suffix, allow_none = True)
    check.check_bool(self.tmp_dir_temp_delete)
    check.check_bool(self.tmp_dir_use_temp)

  def verify(self):
    if self.env_override and self.clean_env:
      raise ValueError(f'Only one of "env_override" or "clean_env" should be given.')

    if self.home_dir and self.home_dir_use_temp:
      raise ValueError(f'Only one of "home_dir" or "home_dir_use_temp" should be given.')

    if self.tmp_dir and self.tmp_dir_use_temp:
      raise ValueError(f'Only one of "tmp_dir" or "tmp_dir_use_temp" should be given.')
    
    
  def resolve_base_env(self):
    if self.clean_env:
      result = os_env.make_clean_env()
    elif self.env_override:
      result = copy.deepcopy(self.env_override)
    else:
      result = os_env.clone_current_env()
    return result

  def resolve_PATH(self, env):
    check.check_dict(env, check.STRING_TYPES, check.STRING_TYPES)
    
    if not self.path_append and not self.path_prepend:
      return None
    PATH = env_var(env, 'PATH')
    if self.path_append:
      PATH.append(self.path_append)
    if self.path_prepend:
      PATH.prepend(self.path_prepend)
    return PATH.value

  _resolved_dir = namedtuple('_resolved_dir', 'where, delete')
  def resolve_home_dir(self):
    if self.home_dir:
      return self._resolved_dir(self.home_dir, False)
    elif self.home_dir_use_temp:
      prefix = self.home_dir_temp_prefix or '-env-override'
      suffix = self.home_dir_temp_suffix or '.home-dir'
      home_dir = tempfile.mkdtemp(prefix = prefix, suffix = suffix)
      filesystem.atexit_remove(home_dir)
      return self._resolved_dir(home_dir, True)
    else:
      return None

  def resolve_tmp_dir(self):
    if self.tmp_dir:
      return self._resolved_dir(self.tmp_dir, False)
    elif self.tmp_dir_use_temp:
      prefix = self.tmp_dir_temp_prefix or '-env-override'
      suffix = self.tmp_dir_temp_suffix or '.tmp-dir'
      tmp_dir = tempfile.mkdtemp(prefix = prefix, suffix = suffix)
      filesystem.atexit_remove(tmp_dir)
      return self._resolved_dir(tmp_dir, True)
    else:
      return None

check.register_class(env_override_options)
