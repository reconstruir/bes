#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.common.check import check
from bes.common.time_util import time_util

from .file_sort_order import file_sort_order

class dirs_cli_options(cli_options):

  def __init__(self, **kargs):
    super(dirs_cli_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'debug': False,
      'dry_run': False,
      'quiet': False,
      'recursive': False,
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
      'debug': bool,
      'dry_run': bool,
      'quiet': bool,
      'recursive': bool,
      'verbose': bool,
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
    return IOError

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    check.check_bool(self.debug)
    check.check_bool(self.dry_run)
    check.check_bool(self.quiet)
    check.check_bool(self.recursive)
    check.check_bool(self.verbose)

check.register_class(dirs_cli_options)
