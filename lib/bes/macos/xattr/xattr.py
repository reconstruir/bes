#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.system.log import logger

from .xattr_error import xattr_error
from .xattr_command import xattr_command

class xattr(object):
  'Class to deal with the macos xattr program.'

  _log = logger('xattr')

  @classmethod
  def keys(clazz, filename):
    'Return all the keys set for filename.'
    check.check_string(filename)

    args = [ '-l', filename ]
    rv = clazz._call_command(args)
    xattr_command.check_result(rv, message = None) #'Failed to get keys for {}'.format(filename))
    keys = [ clazz._parse_key(line) for line in rv.stdout_lines() ]
    return sorted(keys)

  @classmethod
  def _call_command(clazz, args):
    # The default macos xattr in /usr/bin/xattr needs to be used
    # completely independenly of potential virtual env installations
    # of xattr
    env = { 'PYTHONPATH': '', 'PATH': '' }
    return xattr_command.call_command(args,
                                      raise_error = False,
                                      env = env,
                                      check_python_script = False)
  
  @classmethod
  def _parse_key(clazz, s):
    'Return all the keys set for filename.'
    s = s.strip()
    if not s:
      return None
    key, delim, value = s.partition(':')
    assert delim == ':'
    return key.strip()
  
