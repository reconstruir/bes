#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.common.check import check
from bes.script.blurber import blurber

from .git_error import git_error

class git_attributes_file_editor_options(cli_options):

  def __init__(self, **kargs):
    super(git_attributes_file_editor_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'backup': False,
      'blurber': blurber(),
      'debug': False,
      'offset': None,
      'preserve_quotes': True,
      'verbose': False,
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
#      'blurber': blurber,
      'debug': bool,
      'debug': bool,
      'offset': int,
      'preserve_quotes': bool,
      'verbose': bool,
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
    check.check_blurber(self.blurber)
    check.check_bool(self.verbose)
    check.check_bool(self.debug)
    check.check_bool(self.backup)
    check.check_int(self.offset, allow_none = True)
    check.check_bool(self.preserve_quotes)
 
check.register_class(git_attributes_file_editor_options)
