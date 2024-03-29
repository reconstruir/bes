# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import tempfile

from collections import namedtuple

from ..system.check import check
from bes.common.string_util import string_util
from bes.system.log import logger

from .git_exe import git_exe

class git_config(object):
  'A class to deal with git coonfig.'

  log = logger('git')

  @classmethod
  def set_value(clazz, key, value):
    args = [
      'config',
      '--global',
      key,
      string_util.quote_if_needed(value),
    ]
    git_exe.call_git(tempfile.gettempdir(), args, raise_error = False)

  @classmethod
  def unset_value(clazz, key):
    git_exe.call_git(tempfile.gettempdir(), [ 'config', '--global', '--unset', key ], raise_error = False)

  @classmethod
  def get_value(clazz, key):
    rv = git_exe.call_git(tempfile.gettempdir(), [ 'config', '--global', key ], raise_error = False)
    if rv.exit_code == 0:
      return string_util.unquote(rv.stdout.strip())
    else:
      return None

  @classmethod
  def set_identity(clazz, name, email):
    git_exe.call_git(tempfile.gettempdir(), [ 'config', '--global', 'user.name', '"%s"' % (name) ])
    git_exe.call_git(tempfile.gettempdir(), [ 'config', '--global', 'user.email', '"%s"' % (email) ])

  _identity = namedtuple('_identity', 'name, email')
  @classmethod
  def get_identity(clazz):
    return clazz._identity(clazz.get_value('user.name'), clazz.get_value('user.email'))
