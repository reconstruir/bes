#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.common.check import check
from bes.data_output.data_output_options import data_output_options
from bes.data_output.data_output_style import data_output_style
from bes.property.cached_property import cached_property
#from bes.script.blurber import blurber

from .git_error import git_error

class git_cli_common_options(cli_options):

  def __init__(self, **kargs):
    super(git_cli_common_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
#      'blurber': blurber(),
      'debug': False,
      'dry_run': False,
      'output_filename': None,
      'output_style': data_output_style.BRIEF,
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
      'dry_run': bool,
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
    return git_error

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
#    check.check_blurber(self.blurber)
    check.check_bool(self.verbose)
    check.check_bool(self.debug)
    check.check_bool(self.dry_run)
    check.check_string(self.output_filename, allow_none = True)
    check.check_data_output_style(self.output_style, allow_none = True)

  @cached_property  
  def data_output_options(self):
    return data_output_options(output_filename = self.output_filename,
                               style = self.output_style)
    
check.register_class(git_cli_common_options)
