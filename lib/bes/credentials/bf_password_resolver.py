#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import getpass
import os

class bf_password_resolver(object):

  @classmethod
  def resolve(clazz,
              value = None,
              env_var = None,
              keychain_service = None,
              keychain_username = None,
              prompt = 'Enter password: ',
              require = False):
    if value:
      return value

    if env_var:
      v = os.environ.get(env_var)
      if v:
        return v

    if keychain_service and keychain_username:
      try:
        import keyring
        v = keyring.get_password(keychain_service, keychain_username)
        if v:
          return v
      except ImportError:
        pass

    if prompt is not None:
      v = getpass.getpass(prompt)
      if v:
        return v

    if require:
      parts = []
      if env_var:
        parts.append(f'set {env_var}')
      if keychain_service:
        parts.append(f'store in keychain service "{keychain_service}"')
      hint = ' or '.join(parts)
      hint = f' ({hint})' if hint else ''
      raise RuntimeError(f'could not resolve password{hint}')

    return None
