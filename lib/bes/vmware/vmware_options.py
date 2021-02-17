#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.common.dict_util import dict_util
from bes.config.simple_config import simple_config
from bes.credentials.credentials import credentials
from bes.script.blurber import blurber

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

  def __str__(self):
    return str(dict_util.hide_passwords(self.__dict__, [ 'vmrest_password', 'login_password' ]))
    
  @property
  def vmrest_credentials(self):
    return credentials('<cli>', username = self.vmrest_username, password = self.vmrest_password)

  @property
  def login_credentials(self):
    return credentials('<cli>', username = self.login_username, password = self.login_password)

  @classmethod
  def add_argparse_arguments(clazz, p):
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    p.add_argument('-d', '--debug', action = 'store_true', default = False,
                   help = 'Debug mode [ False ]')
    p.add_argument('--vmrest-username', action = 'store', type = str, default = None,
                   help = 'Username for vmrest.  None means generate a random one. [ None ]')
    p.add_argument('--vmrest-password', action = 'store', type = str, default = None,
                   help = 'Password for vmrest.  None means generate a random one. [ None ]')
    p.add_argument('--vmrest-port', action = 'store', type = int, default = 8697,
                   dest = 'vmrest_port',
                   help = 'Port for vmrest [ 8697 ]')
    p.add_argument('--username', action = 'store', type = str, default = None,
                   dest = 'login_username',
                   help = 'Username for vm uer login [ ]')
    p.add_argument('--password', action = 'store', type = str, default = None,
                   dest = 'login_password',
                   help = 'Password for vm user login [ ]')

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
    if 'vmrest_port' in values:
      values['vmrest_port'] = int(values['vmrest_port'])
    return vmware_options(**values)
    
check.register_class(vmware_options)
