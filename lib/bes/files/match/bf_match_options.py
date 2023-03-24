#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.system.check import check

from .bf_match_type import bf_match_type
from ..bfile_path_type import bfile_path_type

class bf_match_options(cli_options):

  def __init__(self, **kargs):
    super().__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'ignore_case': False,
      'match_type': bf_match_type.ANY,
      'path_type': bfile_path_type.ABSOLUTE,
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
    self.match_type = check.check_bf_match_type(self.match_type)
    self.path_type = check.check_bfile_path_type(self.path_type)
    
check.register_class(bf_match_options)
