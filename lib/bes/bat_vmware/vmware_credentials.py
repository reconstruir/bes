#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import subprocess
import random
import os.path as path
import time

from ..system.check import check
from bes.credentials.credentials import credentials
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.system.execute import execute
from bes.system.log import logger

from .vmware_error import vmware_error
from .vmware_util import vmware_util

class vmware_credentials(object):

  _log = logger('vmware_credentials')

  @classmethod
  def make_random_credentials(clazz):
    return credentials('<random>',
                       username = clazz._make_random_username(),
                       password = clazz._make_random_password())


  _INVALID_USERMAME_MSG = '''\
Invalid username.  Only a-z, A-Z, 0-9, dot(.), underline(_), hyphen(-) are permitted, and the length is between 4 and 12.
'''

  _INVALID_PASSWORD_MSG = '''\
Password does not meet complexity requirements:
- Minimum 1 uppercase character
- Minimum 1 lowercase character
- Minimum 1 numeric digit
- Minimum 1 special character(!#$%&'()*+,-./:;<=>?@[]^_`{|}~)
- Length between 8 and 12
'''

  _EXPECT_SCRIPT_MSG_MAP = {
    1: _INVALID_USERMAME_MSG,
    2: _INVALID_PASSWORD_MSG,
  }
  
  _EXPECT_SCRIPT_TEMPLATE = '''\
spawn vmrest -C
expect "Username:"
send "{username}\\n"
expect {{
  "Please type a valid username. Only a-z, A-Z, 0-9, dot(.), underline(_), hyphen(-) are permitted, and the length is between 4 and 12." {{
     exit 1
   }}
  "New password:" {{
    send -- "{password}\\n"
  }}   
}}
expect {{
  "Password does not meet complexity requirements" {{
     exit 2
   }}
  "Retype new password:" {{
    send -- "{password}\\n"
  }}   
}}
expect {{
  "Credential updated successfully" {{
     exit 0
  }}
}}
sleep 1
'''
  
  @classmethod
  def set_credentials(clazz, username, password, num_tries = None):
    check.check_string(username)
    check.check_string(password)
    check.check_int(num_tries, allow_none = True)

    num_tries = num_tries or 10
    
    if num_tries < 1:
      raise vmware_error('Num tries should be between 1 and 10: {}'.format(num_tries))
    if num_tries > 100:
      raise vmware_error('Num tries should be between 1 and 10: {}'.format(num_tries))
    
    last_exception = None
    for i in range(1, num_tries + 1):
      clazz._log.log_d('set_credentials: try {} of {}'.format(i, num_tries))
      try:
        # this happens so much that its not even worth printing unless it passes a threshold
        print_error = i >= 5
        clazz._do_set_credentials(username, password, print_error)
        clazz._log.log_d('set_credentials: try {} of {} succeeded'.format(i, num_tries))
        if clazz._vmrest_config_is_corrupt():
          clazz._log.log_d('set_credentials: vmrest config is corrupt even though set was successfull')
          time.sleep(1.0)
          continue
        if not clazz._vmrest_config_exists():
          clazz._log.log_d('set_credentials: vmrest config does not exists even though set was successfull')
          time.sleep(1.0)
          continue
        return
      except vmware_error as ex:
        clazz._log.log_d('set_credentials: try {} caught {}'.format(i, ex))
        last_exception = ex
        time.sleep(5.0)
    assert last_exception != None
    raise last_exception

  @classmethod
  def _do_set_credentials(clazz, username, password, print_error):
    expect_script = clazz._EXPECT_SCRIPT_TEMPLATE.format(username = username,
                                                         password = password)

    # Remove ~/.vmrestCfg if corrupt
    clazz._vmrest_config_remove_corrupt()

    # Make sure there no stale vmrest processes
    vmware_util.killall_vmrest()
      
    tmp_script = temp_file.make_temp_file(suffix = '.expect', perm = 0o755, content = expect_script, delete = False)
    try:
      cmd = [ 'expect', '-d', tmp_script ]
      rv = execute.execute(cmd, raise_error = False, shell = False)
      clazz._log.log_d('_do_set_credentials: exit_code={} stdout="{}" stderr="{}"'.format(rv.exit_code,
                                                                                          rv.stdout,
                                                                                          rv.stderr))
      if rv.exit_code != 0:
        raise vmware_error(clazz._EXPECT_SCRIPT_MSG_MAP[rv.exit_code])
    finally:
      file_util.remove(tmp_script)

    if clazz._vmrest_config_is_corrupt():
      msg = 'Failed to set credentials.  Corrupt {}'.format(clazz._VMREST_CONFIG_FILENAME)
      if print_error:
        clazz._log.log_i(msg)
      raise vmware_error(msg)
    
  @classmethod
  def _make_random_username(clazz):
    return 'george040'
    names = ( 'john', 'george', 'paul', 'ringo' )
    name = random.choice(names)
    num = str(random.randint(1, 100)).zfill(3)
    return name + num

  @classmethod
  def _make_random_password(clazz):
    return 'n0th#0PPL'
    special_chars = r'#*+'
    lower_part = ( 's3kr', 'h1dd', 'n0th', 'ob8c' )
    upper_part = ( 'K1W1', '0PPL', 'M3L0', 'L3M0' )
    special_char = random.choice(special_chars)
    lower = random.choice(lower_part)
    upper = random.choice(upper_part)
    return lower + '#' + upper

  _VMREST_CONFIG_FILENAME = path.expanduser('~/.vmrestCfg')
  @classmethod
  def _vmrest_config_remove_corrupt(clazz):
    'Make sure there is no corrupt (empty) ~/.vmrestCfg file'
    if clazz._vmrest_config_is_corrupt():
      clazz._log.log_i('Removing corrupt vmrest config: {}'.format(clazz._VMREST_CONFIG_FILENAME))
      file_util.remove(clazz._VMREST_CONFIG_FILENAME)

  @classmethod
  def _vmrest_config_is_corrupt(clazz):
    'Return True if ~/.vmrestCfg is corrupt (empty)'
    if not path.exists(clazz._VMREST_CONFIG_FILENAME):
      return False
    return file_util.is_empty(clazz._VMREST_CONFIG_FILENAME)

  @classmethod
  def _vmrest_config_exists(clazz):
    'Return True if ~/.vmrestCfg is corrupt (empty)'
    return path.exists(clazz._VMREST_CONFIG_FILENAME)
