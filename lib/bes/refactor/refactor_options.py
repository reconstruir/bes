#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.common.check import check
from bes.script.blurber import blurber
from bes.text.word_boundary import word_boundary

from .refactor_error import refactor_error

class refactor_options(cli_options):

  def __init__(self, **kargs):
    super(refactor_options, self).__init__(**kargs)
    
  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'blurber': blurber(),
      'debug': False,
      'dry_run': False,
      'verbose': False,
      'word_boundary': False,
      'word_boundary_chars': word_boundary.CHARS_UNDERSCORE,
      'try_git': False,
      'unsafe': False,
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
      'dry_run': bool,
      'word_boundary': bool,
      'try_git': bool,
      'unsafe': bool,
      'word_boundary_chars': set,
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
    return 'refactor'

  @classmethod
  #@abstractmethod
  def error_class(clazz):
    return refactor_error

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    check.check_blurber(self.blurber)
    check.check_bool(self.verbose)
    check.check_bool(self.debug)
    check.check_bool(self.word_boundary)
    check.check_set(self.word_boundary_chars)
    check.check_bool(self.try_git)
    check.check_bool(self.unsafe)

check.register_class(refactor_options, include_seq = False)
