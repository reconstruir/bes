#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.system.check import check

#from .bfile_filename_match_type import bfile_filename_match_type

class bfile_finder_options(cli_options):

  def __init__(self, **kargs):
    super().__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'relative': True,
      'min_depth': None,
      'max_depth': None,
      'basename_only': False,
      'match_type': bfile_filename_match_type.ANY,
    }

#  @classmethod
#  def find(clazz, root_dir, relative = True, min_depth = None,
#           max_depth = None, file_type = FILE, follow_links = False,
#           match_patterns = None, match_type = None, match_basename = True,
#           match_function = None, match_re = None):
  
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
      'min_depth': int,
      'max_depth': int,
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
    check.check_int(self.min_depth, allow_none = True)
    check.check_int(self.max_depth, allow_none = True)
    self.match_type = check.check_bfile_filename_match_type(self.match_type)
    
check.register_class(bfile_finder_options)
