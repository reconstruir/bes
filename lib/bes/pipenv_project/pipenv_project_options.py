#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.common.check import check
from bes.credentials.credentials import credentials
from bes.data_output.data_output_options import data_output_options
from bes.data_output.data_output_style import data_output_style
from bes.script.blurber import blurber

from .pipenv_project_error import pipenv_project_error

class pipenv_project_options(cli_options):

  def __init__(self, **kargs):
    super(pipenv_project_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'blurber': blurber(),
      'debug': False,
      'output_filename': None,
      'output_style': data_output_style.TABLE,
      'pipenv_version': None,
      'python_exe': None,
      'python_version': None,
      'root_dir': None,
      'verbose': False,
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
      'verbose': bool,
      'debug': bool,
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
    return pipenv_project_error

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    check.check_blurber(self.blurber)
    check.check_bool(self.verbose)
    check.check_bool(self.debug)
    check.check_string(self.pipenv_version, allow_none = True)
    check.check_string(self.root_dir, allow_none = True)
    check.check_string(self.python_exe, allow_none = True)
    check.check_string(self.python_version, allow_none = True)
    check.check_string(self.output_filename, allow_none = True)
    check.check_data_output_style(self.output_style, allow_none = True)
    
check.register_class(pipenv_project_options)
