#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import subprocess
import random

from bes.system.log import logger
from bes.common.check import check
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.credentials.credentials import credentials

from .vmware_error import vmware_error

class vmware_credentials(object):

  _log = logger('vmware_credentials')

  @classmethod
  def make_random_credentials(clazz):
    return credentials('<random>',
                       username = clazz._make_random_username(),
                       password = clazz._make_random_password())
  
  @classmethod
  def set_credentials(clazz, username, password):
    expect_script = '''\
#!/usr/bin/env expect
spawn vmrest -C
expect "Username:"
send "{username}\n"
expect {{
  "Please type a valid username. Only a-z, A-Z, 0-9, dot(.), underline(_), hyphen(-) are permitted, and the length is between 4 and 12." {{
     exit 1
   }}
  "New password:" {{
    send -- "{password}\n"
  }}   
}}
expect {{
  "Password does not meet complexity requirements" {{
     exit 2
   }}
  "Retype new password:" {{
    send -- "{password}\n"
  }}   
}}
'''.format(username = username, password = password)
    
    tmp_script = temp_file.make_temp_file(suffix = '.expect', perm = 0o755, content = expect_script)
    try:
      process = subprocess.Popen(['expect', '-f', tmp_script],
                                 stdin = subprocess.PIPE,
                                 stdout = subprocess.PIPE)
      exit_code = process.wait()
      if exit_code == 0:
        return
      if exit_code == 1:
        raise vmware_error('Invalid username.  Only a-z, A-Z, 0-9, dot(.), underline(_), hyphen(-) are permitted, and the length is between 4 and 12.')
      elif exit_code == 2:
        msg = '''\
Password does not meet complexity requirements:
- Minimum 1 uppercase character
- Minimum 1 lowercase character
- Minimum 1 numeric digit
- Minimum 1 special character(!#$%&'()*+,-./:;<=>?@[]^_`{|}~)
- Length between 8 and 12
'''
        raise vmware_error(msg)
    finally:
      file_util.remove(tmp_script)

  @classmethod
  def _make_random_username(clazz):
    return 'fred'
    names = ( 'john', 'george', 'paul', 'ringo' )
    name = random.choice(names)
    num = str(random.randint(1, 100)).zfill(3)
    return name + num

  @classmethod
  def _make_random_password(clazz):
    return 'FRED#1flint'
    special_chars = r'#%*+-'
    lower_part = ( 's3kr', 'h1dd', 'n0th', 'ob8c' )
    upper_part = ( 'K!W!', '@PPL3', 'M3L0N', 'L3M0N' )
    special_char = random.choice(special_chars)
    lower = random.choice(lower_part)
    upper = random.choice(upper_part)
    num = str(random.randint(0, 9))
    return lower + num + upper + special_char
