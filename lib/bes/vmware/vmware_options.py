#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint

from bes.common.check import check
from bes.common.dict_util import dict_util
from bes.config.simple_config import simple_config
from bes.credentials.credentials import credentials
from bes.script.blurber import blurber

from .vmware_error import vmware_error

class vmware_options(object):
  
  def __init__(self, *args, **kargs):
    self.blurber = blurber()
    self.verbose = False
    self.debug = False
    self.vmrest_username = None
    self.vmrest_password = None
    self.vmrest_port = None
    self.login_username = None
    self.login_password = None
    self.dont_ensure = False
    self.tty = None
    self.clone_vm = False
    self.vm_dir = None
    self.wait_programs_num_tries = 10
    self.wait_programs_sleep_time = 5.0
    for key, value in kargs.items():
      setattr(self, key, value)
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
    
  def __str__(self):
    d = dict_util.hide_passwords(self.__dict__, [ 'vmrest_password', 'login_password' ])
    return pprint.pformat(d)
    
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

  @classmethod
  def from_config_file(clazz, filename):
    '''
    Read vmware options from a config file with this format:
vmware
  vmrest_username: foo
  vmrest_password: sekret
  vmrest_port: 9999
  login_username: fred
  login_password: flintpass
'''
    config = simple_config.from_file(filename)
    if not config.has_section('vmware'):
      raise vmware_error('No section "vmware" found in config file: "{}"'.format(filename))
    section = config.section('vmware')
    values = section.to_dict()

    self._morph_type(values, 'vmrest_port', int)
    self._morph_type(values, 'wait_programs_num_tries', int)
    self._morph_type(values, 'wait_programs_sleep_time', float)
    return vmware_options(**values)

  @classmethod
  def _morph_type(clazz, d, key, type_class):
    if key in values:
      values[key] = type_class(values[key])
  
check.register_class(vmware_options)
