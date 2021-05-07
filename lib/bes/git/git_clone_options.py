#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.common.check import check

from .git_error import git_error

class git_clone_options(cli_options):

  def __init__(self, **kargs):
    super(git_clone_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'branch': None,
      'clean': False,
      'clean_immaculate': False,
      'depth': None,
      'enforce_empty_dir': True,
      'jobs': None,
      'lfs': False,
      'no_network': False,
      'num_tries': 1,
      'reset_to_head': False,
      'retry_wait_seconds': 10.0,
      'shallow_submodules': False,
      'submodule_list': None,
      'submodules': False,
      'submodules_recursive': False,
    }
  
  @classmethod
  #@abstractmethod
  def sensitive_keys(clazz):
    'Return a tuple of keys that are secrets and should be protected from __str__.'
    return None
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return {
      'branch': str,
      'clean': bool,
      'clean_immaculate': bool,
      'depth': int,
      'enforce_empty_dir': bool,
      'jobs': int,
      'lfs': bool,
      'no_network': bool,
      'num_tries': int,
      'reset_to_head': bool,
      'retry_wait_seconds': float,
      'shallow_submodules': bool,
      'submodule_list': list,
      'submodules': bool,
      'submodules_recursive': bool,
    }

  @classmethod
  #@abstractmethod
  def config_file_key(clazz):
    return None

  @classmethod
  #@abstractmethod
  def config_file_env_var_name(clazz):
    return None
  
  @classmethod
  #@abstractmethod
  def config_file_section(clazz):
    return None

  @classmethod
  #@abstractmethod
  def error_class(clazz):
    return git_error

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    check.check_bool(self.enforce_empty_dir)
    check.check_int(self.depth, allow_none = True)
    check.check_bool(self.lfs)
    check.check_int(self.jobs, allow_none = True)
    check.check_bool(self.submodules)
    check.check_bool(self.submodules_recursive)
    check.check_list(self.submodule_list, allow_none = True)
    check.check_string(self.branch, allow_none = True)
    check.check_bool(self.reset_to_head)
    check.check_bool(self.no_network)
    check.check_bool(self.clean)
    check.check_bool(self.clean_immaculate)
    check.check_int(self.num_tries)
    check.check_float(self.retry_wait_seconds)
    check.check_bool(self.shallow_submodules)
  
check.register_class(git_clone_options)
