#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.common.dict_util import dict_util
from rebuild.credentials.credentials import credentials
from bes.script.blurber import blurber

class vmware_client_options(object):
  
  def __init__(self, *args, **kargs):
    self.verbose = False
    self.port = None
    self.blurber = blurber()
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

  @classmethod
  def resolve_with_vault(clazz):
    config = vault_ego.resolve_config()
    v = vault(config)
    username = v.get_secret('cicd/bitbucket', 'EGO_BITBUCKET_USER')
    app_password = v.get_secret('cicd/bitbucket', 'EGO_BITBUCKET_APP_PASSWORD')
    return credentials('<vault>', username = username, app_password = app_password )
    
check.register_class(vmware_client_options)
