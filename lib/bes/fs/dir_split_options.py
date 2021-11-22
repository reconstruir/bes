#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.common.check import check

class dir_split_options(cli_options):

  def __init__(self, **kargs):
    super(dir_split_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'chunk_size': 250,
      'debug': False,
      'prefix': 'split-',
      'recursive': False,
      'verbose': False,
      'dry_run': False,
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
      'chunk_size': int,
      'debug': bool,
      'recursive': bool,
      'verbose': bool,
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
    return IOError

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    check.check_bool(self.verbose)
    check.check_bool(self.dry_run)
    check.check_bool(self.debug)
    check.check_bool(self.recursive)
    check.check_int(self.chunk_size)
    check.check_string(self.prefix)

check.register_class(dir_split_options)
