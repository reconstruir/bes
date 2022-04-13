#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import codecs
import shlex

from bes.system.check import check
from bes.common.string_util import string_util
from bes.debug.hexdump import hexdump
from bes.fs.file_check import file_check
from bes.system.log import logger
from bes.text.text_replace import text_replace

from .xattr_exe_error import xattr_exe_error
from .xattr_exe_error import xattr_exe_permission_error
from .xattr_exe_command import xattr_exe_command

class xattr_exe(object):
  'Class to deal with the macos xattr_exe program.'

  _log = logger('xattr_exe')

  @classmethod
  def has_key(clazz, filename, key):
    'Return all the keys set for filename.'
    check.check_string(filename)
    check.check_string(key)

    args = [ '-p', key, shlex.quote(filename) ]
    rv = clazz._call_xattr_exe(args)
    return rv.exit_code == 0
  
  @classmethod
  def keys(clazz, filename):
    'Return all the keys set for filename.'
    check.check_string(filename)

    args = [ '-l', shlex.quote(filename) ]
    rv = clazz._call_xattr_exe(args)
    xattr_exe_command.check_result(rv, message = 'Failed to get keys for {}'.format(filename))
    keys = [ clazz._parse_key(line) for line in rv.stdout_lines() ]
    return sorted(keys)

  @classmethod
  def _check_permission_error(clazz, result, message):
    clazz._log.log_d('_check_permission_error: result="{}" message="{}"'.format(result, message))
    if result.exit_code != 1:
      return
    if 'Operation not permitted' not in result.stderr:
      return
    raise xattr_exe_permission_error(message)
  
  @classmethod
  def set_bytes(clazz, filename, key, value):
    'Set the value of attribute with key to value for filename.'
    filename = file_check.check_file(filename)
    check.check_string(key)
    check.check_bytes(value)

    hex_value = hexdump.data(value, delimiter = '', line_delimiter = '')
    clazz._log.log_d('set_bytes: hex_value={}'.format(hex_value))
    args = [ '-w', '-x', key, hex_value, shlex.quote(filename) ]
    rv = clazz._call_xattr_exe(args)
    clazz._check_permission_error(rv, 'Permission error setting key="{}" value="{}" for "{}"'.format(key, value, filename))
    xattr_exe_command.check_result(rv, message = 'Failed to set key="{}" value="{}" for "{}"'.format(key, value, filename))

  @classmethod
  def set_string(clazz, filename, key, value):
    'Set the value of attribute with key to value for filename.'
    filename = file_check.check_file(filename)
    check.check_string(key)
    check.check_string(value)

    args = [ '-w', key, value, shlex.quote(filename) ]
    rv = clazz._call_xattr_exe(args)
    clazz._check_permission_error(rv, 'Permission error setting key="{}" value="{}" for "{}"'.format(key, value, filename))
    xattr_exe_command.check_result(rv, message = 'Failed to set key="{}" value="{}" for "{}"'.format(key, value, filename))
    
  @classmethod
  def get_string(clazz, filename, key):
    'Get the value of attribute as a string.'
    filename = file_check.check_file(filename)
    check.check_string(key)

    args = [ '-p', key, shlex.quote(filename) ]
    rv = clazz._call_xattr_exe(args)
    xattr_exe_command.check_result(rv, message = 'Failed to get key="{}" for "{}"'.format(key, filename))
    return rv.stdout.strip()

  @classmethod
  def get_bytes(clazz, filename, key):
    'Get the value of attribute as as bytes.'
    filename = file_check.check_file(filename)
    check.check_string(key)

    args = [ '-p', '-x', key, shlex.quote(filename) ]
    rv = clazz._call_xattr_exe(args)
    clazz._log.log_d('get_bytes: stdout={}'.format(rv.stdout))
    xattr_exe_command.check_result(rv, message = 'Failed to get key="{}" for "{}"'.format(key, filename))
    hex_text = text_replace.replace_white_space(rv.stdout, '')
    clazz._log.log_d('get_bytes: hex_text={}'.format(hex_text))
    return codecs.decode(hex_text, encoding = 'hex')

  @classmethod
  def remove(clazz, filename, key):
    'Remove the attirbute with key from filename.'
    filename = file_check.check_file(filename)
    check.check_string(key)
    
    args = [ '-d', key, shlex.quote(filename) ]
    rv = clazz._call_xattr_exe(args)
    clazz._check_permission_error(rv, 'Permission error removing key="{}" for "{}"'.format(key, filename))
    xattr_exe_command.check_result(rv, message = 'Failed to delete key "{}" for "{}"'.format(key, filename))

  @classmethod
  def clear(clazz, filename):
    'Remove the attirbute with key from filename.'
    filename = file_check.check_file(filename)
    
    args = [ '-c', shlex.quote(filename) ]
    rv = clazz._call_xattr_exe(args)
    clazz._check_permission_error(rv, 'Permission error clearing all values for "{}"'.format(filename))
    xattr_exe_command.check_result(rv, message = 'Failed to clear values for "{}"'.format(filename))
    
  @classmethod
  def _call_xattr_exe(clazz, args):
    # The default macos xattr_exe in /usr/bin/xattr_exe needs to be used
    # completely independenly of potential virtual env installations
    # of xattr_exe
    env = { 'PYTHONPATH': '', 'PATH': '' }
    return xattr_exe_command.call_command(args,
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
