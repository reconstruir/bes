#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.credentials.credentials import credentials
from bes.credentials.bf_password_resolver import bf_password_resolver

class bcli_password_mixin(object):

  @property
  def credentials(self):
    return credentials('<cli>', password = self.password)

  def resolve_password(self,
                       env_var = None,
                       keychain_service = None,
                       keychain_username = None,
                       prompt = 'Enter password: ',
                       require = True):
    self.password = bf_password_resolver.resolve(
      value = self.password,
      env_var = env_var,
      keychain_service = keychain_service,
      keychain_username = keychain_username,
      prompt = prompt,
      require = require,
    )
    return self.password
