#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from ..system.check import check

from .egg_error import egg_error

class egg_options(cli_options):

  def __init__(self, **kargs):
    super(egg_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'debug': False,
      'output_dir': None,
      'project_name': None,
      'setup_filename': None,
      'verbose': False,
      'version_filename': None,
      'include_untracked': False,
    }
  
  @classmethod
  #@abstractmethod
  def sensitive_keys(clazz):
    'Return a tuple of keys that are secrets and should be protected from __str__.'
    return None
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return {
      'debug': bool,
      'verbose': bool,
      'include_untracked': bool,
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
    return egg_error

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'

    check.check_bool(self.debug)
    check.check_bool(self.verbose)
    check.check_string(self.output_dir, allow_none = True)
    check.check_string(self.project_name, allow_none = True)
    check.check_string(self.setup_filename, allow_none = True)
    check.check_string(self.version_filename, allow_none = True)
    
check.register_class(egg_options)
