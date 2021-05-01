#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from .git_config import git_config

class git_identity_cli_command(object):

  @classmethod
  def handle_command(clazz, command, **kargs):
    func = getattr(clazz, command)
    return func(**kargs)
  
  @classmethod
  def set(clazz, name, email):
    check.check_string(name)
    check.check_string(email)
    
    git_config.set_identity(name, email)
    return 0

  @classmethod
  def get(clazz, name_only, email_only):
    check.check_bool(name_only)
    check.check_bool(email_only)
    
    identity = git_config.get_identity()
    if name_only:
      print(identity.name)
    elif email_only:
      print(identity.email)
    else:
      if identity.name and identity.email:
        print('{name}:{email}'.format(name = identity.name, email = identity.email))
      elif identity.name:
        print(identity.name)
      elif identity.email:
        print(identity.email)
      else:
        print('')
    return 0
  
  @classmethod
  def ensure(clazz, name, email):
    check.check_string(name)
    check.check_string(email)

    identity = git_config.get_identity()
    name = identity.name or name
    email = identity.email or email
    if not identity.name or not identity.email:
      clazz.set_identity(name, email)
    return 0
