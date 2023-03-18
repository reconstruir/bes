#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.common.check import check
from bes.credentials.credentials import credentials
from bes.script.blurber import blurber

from .runas_error import runas_error

class runas_options(cli_options):

  def __init__(self, **kargs):
    super(runas_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'blurber': blurber(),
      'verbose': False,
      'debug': False,
      'username': None,
      'password': None,
    }
  
  @classmethod
  #@abstractmethod
  def sensitive_keys(clazz):
    'Return a tuple of keys that are secrets and should be protected from __str__.'
    return ( 'password' )
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return {
      'vmrest_port': int,
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
    return runas_error

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    check.check_blurber(self.blurber)
    check.check_bool(self.verbose)
    check.check_bool(self.debug)
    check.check_string(self.username, allow_none = True)
    check.check_string(self.password, allow_none = True)
  
  @property
  def login_credentials(self):
    if self.username and not self.password:
      raise runas_error('both username and password need to be given.')
    if self.password and not self.username:
      raise runas_error('both password and username need to be given.')
    if not self.username:
      assert not self.password
      return None
    return credentials('<cli>', username = self.username, password = self.password )
  
check.register_class(runas_options)
