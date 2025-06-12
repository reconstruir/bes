#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.credentials.credentials import credentials
from ..system.check import check
from bes.cli.cli_options import cli_options

from .bat_vmware_error import bat_vmware_error

class bat_bat_vmware_session_options(cli_options):
  
  def __init__(self, **kargs):
    super().__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'verbose': False,
      'vmrest_port': None,
      'vmrest_username': None,
      'vmrest_password': None,
    }

  @classmethod
  #@abstractmethod
  def sensitive_keys(clazz):
    'Return list of keys that are secrets and should be protected from __str__.'
    return [ 'vmrest_password' ]
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return {
      'vmrest_port': int,
    }

  @classmethod
  #@abstractmethod
  def config_file_key(clazz):
    return 'config_filename'

  @classmethod
  #@abstractmethod
  def config_file_env_var_name(clazz):
    return 'BES_VMWARE_CONFIG_FILE'
  
  @classmethod
  #@abstractmethod
  def config_file_section(clazz):
    return 'vmware'

  @classmethod
  #@abstractmethod
  def error_class(clazz):
    return bat_vmware_error

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    check.check_bool(self.verbose)
    check.check_int(self.vmrest_port, allow_none = True)
    check.check_string(self.vmrest_username, allow_none = True)
    check.check_string(self.vmrest_password, allow_none = True)
  
  @property
  def vmrest_credentials(self):
    if self.vmrest_username and not self.vmrest_password:
      raise bat_vmware_error('both vmrest_username and vmrest_password need to be given.')
    if self.vmrest_password and not self.vmrest_username:
      raise bat_vmware_error('both vmrest_password and vmrest_username need to be given.')
    if not self.vmrest_username:
      assert not self.vmrest_password
      return None
    return credentials('<cli>', username = self.vmrest_username, password = self.vmrest_password)
    
check.register_class(bat_bat_vmware_session_options)
