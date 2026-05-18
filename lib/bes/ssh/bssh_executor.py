#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.system.check import check

from .bssh_command import bssh_command
from .bssh_error import bssh_error

class bssh_executor(object):
  'Run commands on a remote host over SSH. Secure by default.'

  def __init__(self, key, host, known_hosts_file=None, strict_host_checking=True):
    check.check_string(key)
    check.check_string(host)
    check.check_string(known_hosts_file, allow_none=True)
    check.check_bool(strict_host_checking)
    if not path.exists(key):
      raise bssh_error(f'ssh key not found: {key}')
    self._key = key
    self._host = host
    self._known_hosts_file = known_hosts_file
    self._strict_host_checking = strict_host_checking

  def run(self, remote_cmd):
    'Run remote_cmd on host. Returns stdout string (trailing newline stripped).'
    check.check_string(remote_cmd)
    cmd = ['-i', self._key, '-o', 'BatchMode=yes']
    if not self._strict_host_checking:
      cmd += ['-o', 'StrictHostKeyChecking=no']
    if self._known_hosts_file is not None:
      cmd += ['-o', f'UserKnownHostsFile={self._known_hosts_file}']
    cmd += [self._host, remote_cmd]
    rv = bssh_command.call_command(cmd)
    return rv.stdout.rstrip('\n')
