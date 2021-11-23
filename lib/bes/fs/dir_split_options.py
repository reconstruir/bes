#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.common.check import check
from bes.common.time_util import time_util

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
      'dup_file_timestamp': time_util.timestamp(),
      'dup_file_count': 1,
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
      'dup_file_count': int,
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
    check.check_string(self.dup_file_timestamp)
    check.check_int(self.dup_file_count)

check.register_class(dir_split_options)
