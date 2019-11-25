#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check
from bes.common.string_util import string_util

from .git_basic import git_basic

class git_config(object):
  'class to deal with git config.'

  @classmethod
  def config_set_value(clazz, key, value):
    check.check_string(key)
    check.check_string(value)

    git_basic.call_git('/tmp', [ 'config', '--global', key, value ], raise_error = False)
    
  @classmethod
  def config_unset_value(clazz, key):
    check.check_string(key)

    git_basic.call_git('/tmp', [ 'config', '--global', '--unset', key ], raise_error = False)
    
  @classmethod
  def config_get_value(clazz, key):
    check.check_string(key)

    rv = git_basic.call_git('/tmp', [ 'config', '--global', key ], raise_error = False)
    if rv.exit_code == 0:
      return string_util.unquote(rv.stdout.strip())
    else:
      return None
  
  @classmethod
  def config_set_identity(clazz, name, email):
    check.check_string(name)
    check.check_string(email)

    git_basic.call_git('/tmp', [ 'config', '--global', 'user.name', '"%s"' % (name) ])
    git_basic.call_git('/tmp', [ 'config', '--global', 'user.email', '"%s"' % (email) ])

  _identity = namedtuple('_identity', 'name, email')
  @classmethod
  def config_get_identity(clazz):
    return clazz._identity(clazz.config_get_value('user.name'),
                           clazz.config_get_value('user.email'))
