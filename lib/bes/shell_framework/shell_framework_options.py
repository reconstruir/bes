#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.common.check import check
from bes.script.blurber import blurber

from .shell_framework_error import shell_framework_error
from .shell_framework_defaults import shell_framework_defaults

class shell_framework_options(cli_options):

  def __init__(self, **kargs):
    super(shell_framework_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'blurber': blurber(),
      'verbose': False,
      'debug': False,
      'address': shell_framework_defaults.ADDRESS,
      'framework_basename': shell_framework_defaults.FRAMEWORK_BASENAME,
      'revision_basename': shell_framework_defaults.REVISION_BASENAME,
      'revision': shell_framework_defaults.REVISION,
      'dest_dir': shell_framework_defaults.DEST_DIR,
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
    return shell_framework_error

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    check.check_blurber(self.blurber)
    check.check_bool(self.verbose)
    check.check_bool(self.debug)
    check.check_string(self.address)
    check.check_string(self.framework_basename)
    check.check_string(self.revision_basename)
    check.check_string(self.revision)
    check.check_string(self.dest_dir)
    
check.register_class(shell_framework_options)
