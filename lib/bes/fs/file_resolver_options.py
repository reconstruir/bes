#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.common.check import check
from bes.common.time_util import time_util

from .file_sort_order import file_sort_order

class file_resolver_options(cli_options):

  def __init__(self, **kargs):
    super(file_resolver_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'recursive': True,
      'sort_order': None,
      'sort_reverse': False,
      'limit': None,
      'match_patterns': None,
      'match_type': None,
      'match_basename': True,
      'match_function': None,
      'match_re': None
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
      'recursive': bool,
      'sort_order': file_sort_order,
      'sort_reverse': bool,
      'limit': int,
      'exclude_patterns': list,
      'match_patterns': list,
      #'match_type': None,
      #'match_basename': True,
      #'match_function': None,
      #'match_re': list,
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
    check.check_bool(self.recursive)
    check.check_file_sort_order(self.sort_order, allow_none = True)
    check.check_bool(self.sort_reverse)
    check.check_int(self.limit, allow_none = True)
    check.check_string_seq(self.match_patterns, allow_none = True)
    #check.check_string_seq(self.match_type, allow_none = True)
    check.check_bool(self.match_basename)
    check.check_function(self.match_function, allow_none = True)
    check.check_string_seq(self.match_re, allow_none = True)
    
check.register_class(file_resolver_options)
