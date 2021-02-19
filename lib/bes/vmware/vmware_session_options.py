#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.dict_util import dict_util
from bes.credentials.credentials import credentials
from bes.common.check import check
from bes.script.blurber import blurber
from bes.cli.cli_options import cli_options

from .vmware_error import vmware_error

class vmware_session_options(cli_options):
  
  def __init__(self, **kargs):
    super(vmware_session_options, self).__init__(**kargs)

  #@abstractmethod
  def default_values(self):
    'Return a dict of defaults for these options.'
    return {
      'verbose': False,
      'vmrest_port': None,
      'vmrest_username': None,
      'vmrest_password': None,
    }

  #@abstractmethod
  def sensitive_keys(self):
    'Return list of keys that are secrets and should be protected from __str__.'
    return [ 'vmrest_password' ]
  
  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    check.check_bool(self.verbose)
    check.check_int(self.vmrest_port, allow_none = True)
    check.check_string(self.vmrest_username, allow_none = True)
    check.check_string(self.vmrest_password, allow_none = True)

  #@abstractmethod
  def value_type_hints(self):
    return {
      'vmrest_port': int,
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
    
check.register_class(vmware_session_options)
