#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import multiprocessing
import os
import re
import signal
import subprocess
import time
from collections import namedtuple
from bes.compat.Queue import Empty as QueueEmptyException

from bes.system.log import logger
from ..system.check import check

from .bat_vmware_error import bat_vmware_error
from .bat_vmware_util import bat_vmware_util

class bat_vmware_server(object):

  _log = logger('bat_vmware_server')

  _info = namedtuple('_info', 'address, pid, version')
  
  def __init__(self, port = None):
    self._log.log_d('bat_vmware_server(id={} self={}, port={})'.format(id(self), self, port))
    self._requested_port = port
    self.address = None
    self._process = None
    self._address_notification = multiprocessing.Queue()
    self.version = None
    self.pid = None

  def _vmrest_process(self):
    # Make sure there no stale vmrest processes
    self._log.log_d('_vmrest_process: killing any stale vmreset')
    bat_vmware_util.killall_vmrest()

    cmd = [ 'vmrest' ]
    if self._requested_port:
      cmd.extend([ '-p', str(self._requested_port) ])
    process = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = False)
    self.pid = process.pid
    self._log.log_d('pid={}'.format(self.pid))
    while True:
      next_line = process.stdout.readline().strip().decode()
      if next_line:
        self._log.log_d(f'next_line="{next_line}"')
      else:
        continue
      if 'Failed to launch vmrest' in next_line:
        self._log.log_e('failed to launch vmrest(1): cmd="{}"'.format(' '.join(cmd)))
        return 1
      elif 'Unable to get configurations: Bad response' in next_line:
        self._log.log_e('failed to launch vmrest(2): cmd="{}"'.format(' '.join(cmd)))
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
    num_tries = 5
    address_timeout = 5.0
    sleep_timeout = 1.0
    info = None
    for i in range(1, num_tries + 1):
      label = '{} of {}'.format(i, num_tries)
      self._log.log_d('{}: process attempt'.format(label))
      self._process = multiprocessing.Process(name = 'bat_vmware_server', target = self._vmrest_process)
      self._process.daemon = True
      self._process.start()
      self._log.log_d('{}: waiting for server info'.format(label))
      try:
        info = self._info(*self._address_notification.get(timeout = address_timeout))
        self._log.log_d('{}: got server info: {}'.format(label, info))
        break
      except QueueEmptyException as ex:
        self._log.log_d('{}: timeout getting server info'.format(label))
        self._log.log_d('{}: sleeping {}'.format(label, sleep_timeout))
        time.sleep(sleep_timeout)
      
    if not info:
      raise bat_vmware_error('Failed to start server after {} tries.'.format(num_tries))
      
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
