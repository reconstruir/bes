#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.system.check import check

from .bfile_filename_match_type import bfile_filename_match_type

class bfile_filename_matcher_options(cli_options):

  def __init__(self, **kargs):
    super().__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'ignore_case': False,
      'basename_only': False,
      'match_type': bfile_filename_match_type.ANY,
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
      'ignore_case': bool,
      'basename_only': bool,
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
    return RuntimeError

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    check.check_bool(self.ignore_case)
    check.check_bool(self.basename_only)
    self.match_type = check.check_bfile_filename_match_type(self.match_type)
    
check.register_class(bfile_filename_matcher_options)
