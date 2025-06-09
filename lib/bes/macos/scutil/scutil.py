#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger

from .scutil_error import scutil_error

class scutil(object):
  'Class to deal with the macos scutil program.'

  _log = logger('scutil')

  @classmethod
  def get_value(clazz, key):
    'Get a value.'
    check.check_string(key)

    host.check_is_macos()
    
    cmd = [ 'scutil', '--get', key ]
    rv = execute.execute(cmd, raise_error = False)
    # check for "not set"
    if rv.exit_code == 1:
      return None
    if rv.exit_code != 0:
      cmd_flat = ' '.join(cmd)
      msg = 'scutil command failed: {} - {}\n{}'.format(cmd_flat,
                                                          rv.exit_code,
                                                          rv.stdout)
      raise scutil_error(msg, status_code = rv.exit_code)
    return rv.stdout.strip()

  @classmethod
  def set_value(clazz, key, value):
    'Set a value.'
    check.check_string(key)
    check.check_string(value)

    host.check_is_macos()
    
    cmd = [ 'scutil', '--set', key, value ]
    rv = execute.execute(cmd, raise_error = False)
    if rv.exit_code != 0:
      cmd_flat = ' '.join(cmd)
      msg = 'scutil command failed: {} - {}\n{}'.format(cmd_flat,
                                                          rv.exit_code,
                                                          rv.stdout)
      raise scutil_error(msg, status_code = rv.exit_code)
