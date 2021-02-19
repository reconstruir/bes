#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_options import cli_options
from bes.common.check import check
from bes.credentials.credentials import credentials
from bes.script.blurber import blurber

from .vmware_error import vmware_error

class vmware_options(cli_options):

  def __init__(self, **kargs):
    super(vmware_options, self).__init__(**kargs)

  #@abstractmethod
  def default_values(self):
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
      'dont_ensure': False,
      'tty': None,
      'clone_vm': False,
      'vm_dir': None,
      'wait_programs_num_tries': 10,
      'wait_programs_sleep_time': 5.0,
    }
  
  #@abstractmethod
  def sensitive_keys(self):
    'Return list of keys that are secrets and should be protected from __str__.'
    return [ 'vmrest_password', 'login_password' ]
  
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
    check.check_bool(self.dont_ensure)
    check.check_bool(self.dont_ensure)
    check.check_string(self.tty, allow_none = True)
    check.check_bool(self.clone_vm)
    check.check_string(self.vm_dir, allow_none = True)
    check.check_int(self.wait_programs_num_tries)
    check.check_float(self.wait_programs_sleep_time)

  #@abstractmethod
  def value_type_hints(self):
    return {
      'vmrest_port': int,
      'wait_programs_num_tries': int,
      'wait_programs_sleep_time': float,
    }

  #@abstractmethod
  def config_file_key(self):
    return 'config_filename'

  #@abstractmethod
  def config_file_section(self):
    return 'vmware'

  #@abstractmethod
  def error_class(self):
    return vmware_error
  
  @property
  def vmrest_credentials(self):
    if self.vmrest_username and not self.vmrest_password:
      raise vmware_error('both vmrest_username and vmrest_password need to be given.')
    if self.vmrest_password and not self.vmrest_username:
      raise vmware_error('both vmrest_password and vmrest_username need to be given.')
    if not self.vmrest_username:
      assert not self.vmrest_password
      return None
    return credentials('<cli>', username = self.vmrest_username, password = self.vmrest_password)

  @property
  def login_credentials(self):
    if self.login_username and not self.login_password:
      raise vmware_error('both login_username and login_password need to be given.')
    if self.login_password and not self.login_username:
      raise vmware_error('both login_password and login_username need to be given.')
    if not self.login_username:
      assert not self.login_password
      return None
    return credentials('<cli>', username = self.login_username, password = self.login_password)
  
check.register_class(vmware_options)
