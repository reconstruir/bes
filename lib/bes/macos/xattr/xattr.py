#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.debug.hexdump import hexdump
from bes.fs.file_check import file_check
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
    rv = clazz._call_xattr(args)
    xattr_command.check_result(rv, message = 'Failed to get keys for {}'.format(filename))
    keys = [ clazz._parse_key(line) for line in rv.stdout_lines() ]
    return sorted(keys)

  @classmethod
  #@abstractmethod
  def set_bytes(clazz, filename, key, value):
    'Set the value of attribute with key to value for filename.'
    filename = file_check.check_file(filename)
    check.check_string(key)
    check.check_bytes(value)

    hex_value = hexdump.data(value, delimiter = '')
    args = [ '-w', '-x', key, hex_value, filename ]
    rv = clazz._call_xattr(args)
    xattr_command.check_result(rv, message = 'Failed to set key="{}" value="{}" for "{}"'.format(key, value, filename))

  @classmethod
  #@abstractmethod
  def set_string(clazz, filename, key, value):
    'Set the value of attribute with key to value for filename.'
    filename = file_check.check_file(filename)
    check.check_string(key)
    check.check_string(value)

    args = [ '-w', key, value, filename ]
    rv = clazz._call_xattr(args)
    xattr_command.check_result(rv, message = 'Failed to set key="{}" value="{}" for "{}"'.format(key, value, filename))
    
  @classmethod
  #@abstractmethod
  def get_string(clazz, filename, key):
    'Get the value of attribute as a string.'
    filename = file_check.check_file(filename)
    check.check_string(key)

    args = [ '-p', key, filename ]
    rv = clazz._call_xattr(args)
    xattr_command.check_result(rv, message = 'Failed to get key="{}" for "{}"'.format(key, filename))
    return rv.stdout.strip()

  @classmethod
  #@abstractmethod
  def get_value(clazz, filename, key, value):
    'Get the value of attribute with key to value for filename.'
    filename = file_check.check_file(filename)
    check.check_string(key)
    check.check_bytes(value)

    hex_value = hexdump.data(value, delimiter = '')
    args = [ '-w', '-x', key, hex_value, filename ]
    rv = clazz._call_xattr('-w', key, hex_value, filename)
    xattr_command.check_result(rv, message = 'Failed to set key="{}" value="{}" for "{}"'.format(key, value, filename))
    
  @classmethod
  def _call_xattr(clazz, args, codec = None):
    # The default macos xattr in /usr/bin/xattr needs to be used
    # completely independenly of potential virtual env installations
    # of xattr
    env = { 'PYTHONPATH': '', 'PATH': '' }
    return xattr_command.call_command(args,
                                      raise_error = False,
                                      env = env,
                                      check_python_script = False,
                                      codec = codec)
  
  @classmethod
  def _parse_key(clazz, s):
    'Return all the keys set for filename.'
    s = s.strip()
    if not s:
      return None
    key, delim, value = s.partition(':')
    assert delim == ':'
    return key.strip()
