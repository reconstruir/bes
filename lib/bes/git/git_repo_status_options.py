#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.common.check import check

from .git_error import git_error

class git_repo_status_options(cli_options):

  def __init__(self, **kargs):
    super(git_repo_status_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'no_remote_update': False,
      'include_untracked': False,
      'force_show': False,
      'verbose': False,
      'debug': False,
      'short_hash': True,
      'num_tries': 10,
      'retry_sleep_time': 0.100,
      'num_threads': 10,
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
      'no_remote_update': bool,
      'include_untracked': bool,
      'force_show': bool,
      'verbose': bool,
      'debug': bool,
      'short_hash': bool,
      'num_tries': int,
      'num_threads': int,
      'retry_sleep_time': float,
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
    check.check_bool(self.no_remote_update)
    check.check_bool(self.include_untracked)
    check.check_bool(self.force_show)
    check.check_bool(self.verbose)
    check.check_bool(self.debug)
  
check.register_class(git_repo_status_options)
