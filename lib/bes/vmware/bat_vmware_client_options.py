#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.common.dict_util import dict_util
from bes.credentials.credentials import credentials
from bes.system.env_var import os_env_var
from bes.script.blurber import blurber

class bat_vmware_client_options(object):
  
  def __init__(self, *args, **kargs):
    self.verbose = False
    self.port = 8697
    self.blurber = blurber()
    self.hostname = None
    self.username = None
    self.password = None
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_bool(self.verbose)
    check.check_blurber(self.blurber)
    check.check_int(self.port, allow_none = True)
    check.check_string(self.hostname, allow_none = True)
    check.check_string(self.username, allow_none = True)
    check.check_string(self.password, allow_none = True)

  def __str__(self):
    return str(dict_util.hide_passwords(self.__dict__, [ 'password' ]))
    
  @property
  def address(self):
    return ( self.hostname, self.port )

  @property
  def auth(self):
    username = self.username or os_env_var('BES_VMWARE_USERNAME').value_if_set
    password = self.password or os_env_var('BES_VMWARE_PASSWORD').value_if_set
    return credentials('<cli>', username = username, password = password)
    
check.register_class(bat_vmware_client_options)
