#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.system.check import check

from bes.bcli.bcli_options import bcli_options
from bes.bcli.bcli_options_desc import bcli_options_desc

from bes.bcli.bcli_simple_type_item_list import bcli_simple_type_item_list
from bes.bcli.bcli_simple_type_item import bcli_simple_type_item

from .bf_match_type import bf_match_type
from ..bf_path_type import bf_path_type

class _caca_options_desc(bcli_options_desc):

  def __init__(self):
    super().__init__()

  #@abstractmethod
  def name(self):
    return '_caca_options_desc'
  
  #@abstractmethod
  def types(self):
    return bcli_simple_type_item_list([
      bcli_simple_type_item('bf_match_type', lambda: bf_match_type, bf_match_type.parse_string),
      bcli_simple_type_item('bf_path_type', lambda: bf_path_type, bf_path_type.parse_string),
    ])

  #@abstractmethod
  def options_desc(self):
    return '''
ignore_case bool default=False
match_type bf_match_type default=ANY
path_type bf_path_type default=ABSOLUTE
'''
  
  #@abstractmethod
  def variables(self):
    return {
      '_var_foo': lambda: '42',
      '_var_bar': lambda: '666',
    }

class bf_match_options(bcli_options):
  def __init__(self, **kwargs):
    #print(f'CACA: kwargs={kwargs}', flush = True)
    super().__init__(_caca_options_desc(), **kwargs)

class xbf_match_options(cli_options):

  def __init__(self, **kargs):
    super().__init__(**kargs)

#bcli_simple_type_item(namedtuple('bcli_simple_type_item', 'name, type_function, parse_function')):

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
