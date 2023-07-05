#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from ..system.check import check
from bes.data_output.data_output_options_mixin import data_output_options_mixin

from .git_error import git_error

class git_cli_common_options(cli_options, data_output_options_mixin):

  def __init__(self, **kargs):
    super().__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'debug': False,
      'dry_run': False,
      'output_filename': None,
      'output_style': 'brief',
      'verbose': False,
    }
  
  @classmethod
  #@abstractmethod
  def sensitive_keys(clazz):
    'Return a tuple of keys that are secrets and should be protected from __str__.'
    None
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return {
      'verbose': bool,
      'debug': bool,
      'dry_run': bool,
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
    check.check_bool(self.verbose)
    check.check_bool(self.debug)
    check.check_bool(self.dry_run)
    check.check_string(self.output_filename, allow_none = True)
    check.check_data_output_style(self.output_style, allow_none = True)

check.register_class(git_cli_common_options)
