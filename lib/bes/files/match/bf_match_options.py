#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.system.check import check

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from bes.bcli.bcli_type_list import bcli_type_list
from bes.bcli.bcli_type_i import bcli_type_i

from .bf_match_type import bf_match_type
from ..bf_path_type import bf_path_type

class _bf_match_options_desc(bcli_options_desc):

  class _bf_type_bf_match_type(bcli_type_i):

    #@abstractmethod
    def name_str(self):
      return 'bf_match_type'

    #@abstractmethod
    def type_function(self):
      return lambda: bf_match_type

    #@abstractmethod
    def parse(self, text):
      return bf_match_type.parse_string(text)

    #@abstractmethod
    def check(self, value, allow_none = False):
      return check.check_bf_match_type(value, allow_none = allow_none)

  class _bf_type_bf_path_type(bcli_type_i):

    #@abstractmethod
    def name_str(self):
      return 'bf_path_type'

    #@abstractmethod
    def type_function(self):
      return lambda: bf_path_type

    #@abstractmethod
    def parse(self, text):
      return bf_path_type.parse_string(text)

    #@abstractmethod
    def check(self, value, allow_none = False):
      return check.check_bf_path_type(value, allow_none = allow_none)
    
  def __init__(self):
    super().__init__()

  #@abstractmethod
  def name(self):
    return '_bf_match_options_desc'
  
  #@abstractmethod
  def types(self):
    return bcli_type_list([
      self._bf_type_bf_match_type(),
      self._bf_type_bf_path_type(),
    ])

  #@abstractmethod
  def options_desc(self):
    return '''
ignore_case bool          default=False
 match_type bf_match_type default=ANY
  path_type bf_path_type  default=ABSOLUTE
'''
  
  #@abstractmethod
  def variables(self):
    return {
      '_var_foo': lambda: '42',
      '_var_bar': lambda: '666',
    }

class bf_match_options(bcli_options):
  def __init__(self, **kwargs):
    super().__init__(_bf_match_options_desc(), **kwargs)

class xbf_match_options(cli_options):

  def __init__(self, **kargs):
    super().__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'ignore_case': False,
      'match_type': bf_match_type.ANY,
      'path_type': bf_path_type.ABSOLUTE,
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
    self.path_type = check.check_bf_path_type(self.path_type)
    
check.register_class(bf_match_options)
