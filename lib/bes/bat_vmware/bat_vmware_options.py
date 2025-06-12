#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from ..system.check import check
from bes.credentials.credentials import credentials
from bes.script.blurber import blurber

from .bat_vmware_error import bat_vmware_error

class bat_vmware_options(cli_options):

  def __init__(self, **kargs):
    super(bat_vmware_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return {
      'blurber': blurber(),
      'verbose': False,
      'debug': False,
      'vmrest_username': None,
      'vmrest_password': None,
      'vmrest_port': None,
      'login_username': None,
      'login_password': None,
      'tty': None,
      'vm_dir': None,
    }
  
  @classmethod
  #@abstractmethod
  def sensitive_keys(clazz):
    'Return a tuple of keys that are secrets and should be protected from __str__.'
    return ( 'vmrest_password', 'login_password' )
  
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
    check.check_blurber(self.blurber)
    check.check_bool(self.verbose)
    check.check_bool(self.debug)
    check.check_string(self.vmrest_username, allow_none = True)
    check.check_string(self.vmrest_password, allow_none = True)
    check.check_int(self.vmrest_port, allow_none = True)
    check.check_string(self.login_username, allow_none = True)
    check.check_string(self.login_password, allow_none = True)
    check.check_string(self.tty, allow_none = True)
    check.check_string(self.vm_dir, allow_none = True)
  
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

  @property
  def login_credentials(self):
    if self.login_username and not self.login_password:
      raise bat_vmware_error('both login_username and login_password need to be given.')
    if self.login_password and not self.login_username:
      raise bat_vmware_error('both login_password and login_username need to be given.')
    if not self.login_username:
      assert not self.login_password
      return None
    return credentials('<cli>', username = self.login_username, password = self.login_password)
  
  def resolve_login_username(self, vm_name):
    check.check_string(vm_name)
    config = self.config_file
    if not config:
      return self.login_username
    has = config.has_section(vm_name)
    if config.has_section(vm_name):
      return config.get_value_with_default(vm_name, 'login_username', self.login_username)
    return self.login_username

  def resolve_login_password(self, vm_name):
    check.check_string(vm_name)
    config = self.config_file
    if not config:
      return self.login_password
    if config.has_section(vm_name):
      return config.get_value_with_default(vm_name, 'login_password', self.login_password)
    return self.login_password

  def resolve_login_credentials(self, vm_name):
    login_username = self.resolve_login_username(vm_name)
    login_password = self.resolve_login_password(vm_name)
    if login_username and not login_password:
      raise bat_vmware_error('both login_username and login_password need to be given.')
    if login_password and not login_username:
      raise bat_vmware_error('both login_password and login_username need to be given.')
    if not login_username:
      assert not login_password
      return None
    return credentials('<cli>', username = login_username, password = login_password)
  
check.register_class(bat_vmware_options)
