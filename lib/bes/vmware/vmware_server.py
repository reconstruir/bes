#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import multiprocessing
import os
import re
import signal
import subprocess
import time
from collections import namedtuple

from os import path

from bes.system.log import logger
from bes.common.check import check
from bes.compat.StringIO import StringIO
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file

from .vmware_error import vmware_error

class vmware_server(object):

  _log = logger('vmware_server')

  _info = namedtuple('_info', 'address, pid, version')
  
  def __init__(self, port = None):
    self._log.log_d('vmware_server(id={} self={}, port={})'.format(id(self), self, port))
    self._requested_port = port
    self.address = None
    self._process = None
    self._address_notification = multiprocessing.Queue()
    self.version = None
    self.pid = None

  def _vmrest_process(self):
    cmd = [ 'vmrest' ]
    if self._requested_port:
      cmd.extend([ '-p', str(self._requested_port) ])
    process = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = False)
    self.pid = process.pid
    self._log.log_d('pid={}'.format(self.pid))
    while True:
      next_line = process.stdout.readline().strip()
      if next_line:
        self._log.log_d('next_line="{}"'.format(next_line))
      else:
        continue
      if 'Failed to launch vmrest' in next_line:
        self._log.log_e('failed to launch vmrest: cmd="{}"'.format(' '.join(cmd)))
        return 1
      elif next_line.startswith('vmrest '):
        self.version = self._parse_version(next_line)
        self._log.log_i('vmrest version: {}'.format(self.version))
      elif 'Serving HTTP' in next_line:
        address = self._parse_server_address(next_line)
        self._log.log_i('launched vmrest on {}'.format(address))
        self._address_notification.put( ( address, self.pid, self.version ) )
        break
    self._log.log_d('waiting for process')
    try:
      exit_code = process.wait()
      self._log.log_d('process returns with exit_code {}'.format(exit_code))
      return exit_code
    except KeyboardInterrupt as ex:
      return 0

  @classmethod
  def _parse_server_address(clazz, s):
    f = re.findall(r'^Serving\sHTTP\son\s([0-9]+\.[0-9]+\.[0-9]\.[0-9]+):(.*)$', s)
    return f[0]

  @classmethod
  def _parse_version(clazz, s):
    f = re.findall(r'^vmrest\s(.+)\s.*$', s)
    return f[0]
  
  def start(self):
    self._process = multiprocessing.Process(name = 'vmware_server', target = self._vmrest_process)
    self._process.daemon = True
    self._process.start()
    self._log.log_d('waiting for address notification')
    info = self._info(*self._address_notification.get())
    self._log.log_d('got info notification: {}'.format(info))
    self.address = info.address
    self.pid = info.pid
    self.version = info.version
  
  def stop(self):
    self._log.log_d('sending SIGINT')
    os.kill(self.pid, signal.SIGINT)
    self._log.log_d('calling join')
    self._process.join()
    self._log.log_d('join returns')

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
