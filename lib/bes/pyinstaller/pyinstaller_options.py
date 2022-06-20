#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from ..system.check import check
from bes.script.blurber import blurber

from .pyinstaller_error import pyinstaller_error
from .pyinstaller_log_level import pyinstaller_log_level
from .pyinstaller_defaults import pyinstaller_defaults

class pyinstaller_options(cli_options):

  def __init__(self, **kargs):
    super(pyinstaller_options, self).__init__(**kargs)
    
  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'blurber': blurber(),
      'build_dir': pyinstaller_defaults.BUILD_DIR,
      'clean': True,
      'debug': False,
      'excludes': None,
      'hidden_imports': None,
      'log_level': pyinstaller_defaults.LOG_LEVEL,
      'python_version': '3.8',
      'verbose': False,
      'windowed': pyinstaller_defaults.WINDOWED,
      'osx_bundle_identifier': None,
      'replace_env': None,
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
      'clean': bool,
      'debug': bool,
      'excludes': list,
      'hidden_imports': list,
      'verbose': bool,
      'windowed': bool,
      'replace_env': dict,
    }

  @classmethod
  #@abstractmethod
  def config_file_key(clazz):
    return 'config_filename'

  @classmethod
  #@abstractmethod
  def config_file_env_var_name(clazz):
    return None
  
  @classmethod
  #@abstractmethod
  def config_file_section(clazz):
    return 'pyinstaller'

  @classmethod
  #@abstractmethod
  def error_class(clazz):
    return pyinstaller_error

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    check.check_blurber(self.blurber)
    check.check_bool(self.verbose)
    check.check_bool(self.debug)
    check.check_string(self.build_dir, allow_none = True)
    check.check_string(self.python_version)
    check.check_bool(self.clean)
    check.check_bool(self.windowed)
    check.check_string(self.osx_bundle_identifier, allow_none = True)
    self.log_level = check.check_pyinstaller_log_level(self.log_level)
    check.check_dict(self.replace_env, allow_none = True)
    
check.register_class(pyinstaller_options, include_seq = False)
