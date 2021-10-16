#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.common.check import check
from bes.credentials.credentials import credentials
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
      'verbose': False,
      'debug': False,
      'pipenv_version': 'latest',
      'root_dir': None,
      'python_version': None,
      'name': None,
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
    check.check_string(self.pipenv_version)
    check.check_string(self.root_dir, allow_none = True)
    check.check_string(self.python_version, allow_none = True)
    check.check_string(self.name, allow_none = True)

  def resolve_root_dir(self):
    if self.root_dir:
      return self.root_dir
    import os
    import os.path as path
    return path.join(os.getcwd(), 'BES_PIPENV_ROOT')
    
check.register_class(pipenv_project_options)
