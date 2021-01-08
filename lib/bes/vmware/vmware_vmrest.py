#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import subprocess
import multiprocessing

from os import path

from bes.system.log import logger
from bes.common.check import check

class vmware_vmrest(object):

  _log = logger('vmware_vmrest')
  
  def __init__(self, port = None):
    self._log.log_i('vmware_vmrest(id={} self={}, port={})'.format(id(self), self, port))
    self._requested_port = port
    self.address = None
    self._process = None
    self._port_queue = multiprocessing.Queue()
  
  def _vmrest_process(self):
    print('hi; here')
    cmd = [
      'vmrest',
      '-p', '9000',
    ]
    #cwd = cwd, env = env, 
    process = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = False)
    while True:
      nextline = process.stdout.readline()
      print('next_line: {}'.format(nextline))
    print('HI')
#    stdout, stderr = process.communicate()
#    exit_code = process.wait()

  def start(self):
    self._process = multiprocessing.Process(name = 'vmware_vmrest', target = self._vmrest_process)
    self._process.daemon = True
    self._process.start()
    self._log.log_i('waiting for port known notification')
    self.address = self._port_queue.get()
  
  def stop(self):
    self._process.terminate()
    self._process.join()
