#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.common.check import check
from bes.credentials.credentials import credentials
from bes.script.blurber import blurber
from bes.data_output.data_output_style import data_output_style
from bes.data_output.data_output_options import data_output_options
from bes.property.cached_property import cached_property

from .pip_error import pip_error

class pip_project_options(cli_options):

  def __init__(self, **kargs):
    super(pip_project_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'blurber': blurber(),
      'verbose': False,
      'debug': False,
      'root_dir': None,
      'python_exe': None,
      'python_version': None,
      'output_style': data_output_style.TABLE,
      'output_filename': None,
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
#      'output_style': data_output_style,
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
    return pip_error

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    check.check_blurber(self.blurber)
    check.check_bool(self.verbose)
    check.check_bool(self.debug)
    check.check_string(self.root_dir, allow_none = True)
    check.check_string(self.python_version, allow_none = True)
    check.check_string(self.python_exe, allow_none = True)
    check.check_string(self.output_filename, allow_none = True)
    check.check_data_output_style(self.output_style, allow_none = True)

  def resolve_python_exe(self):
    if self.python_exe:
      return self.python_exe

    from .python_exe import python_exe
    if not self.python_version:
      exe = python_exe.default_exe()
      if not exe:
        raise pip_error('No default python found')
    else:
      exe = python_exe.find_version(self.python_version)
      if not exe:
        raise pip_error('No python found for version "{}"'.format(self.python_version))
    return exe

  def resolve_root_dir(self):
    if self.root_dir:
      return self.root_dir
    import os
    import os.path as path
    return path.join(os.getcwd(), 'BES_PIP_ROOT')

  @cached_property  
  def data_output_options(self):
    return data_output_options(output_filename = self.output_filename,
                               style = self.output_style)
    
check.register_class(pip_project_options)
