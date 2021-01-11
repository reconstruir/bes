#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse

from bes.system.log import logger
from bes.common.string_util import string_util
from bes.compat.input import input
from bes.system.log import log

from .vmware_server_controller import vmware_server_controller

class vmware_server_shell(object):

  _log = logger('vmware_server_shell')
  
  def __init__(self):
    self._controller = vmware_server_controller()
  
  def main(self, args = None, shell_args = None):
    ap = argparse.ArgumentParser()
    ap.add_argument('-p', '--port', action = 'store', default = None, type = int,
                    help = 'The port to bind to [ None ]')
    parsed_args = ap.parse_args(args = args)
    if parsed_args.port:
      self._command_start([ 'start', str(parsed_args.port)])
    if shell_args:
      self._handle_command(shell_args)
    while True:
      if not self._command_loop():
        break
    self._controller.stop()
    return 0

  def _command_loop(self):
    try:
      cmd = string_util.split_by_white_space(input('CMD> '), strip = True)
      if cmd:
        return self._handle_command(cmd)
    except KeyboardInterrupt as ex:
      return False
    except EOFError as ex:
      return False
    return True

  def _handle_command(self, cmd):
    if cmd[0] == 'stop':
      return self._command_stop(cmd)
    elif cmd[0] == 'start':
      return self._command_start(cmd)
    elif cmd[0] == 'address':
      return self._command_address(cmd)
    elif cmd[0] == 'pid':
      return self._command_pid(cmd)
    elif cmd[0] == 'info':
      return self._command_info(cmd)
    elif cmd[0] == 'version':
      return self._command_version(cmd)
    elif cmd[0] == 'quit':
      return self._command_quit(cmd)
    else:
      print('unknown command: "{}"'.format(cmd))
    return True
  
  def _command_stop(self, cmd):
    self._controller.stop()
    return True

  def _command_start(self, cmd):
    if len(cmd) > 1:
      port = int(cmd[1])
    else:
      port = None
    self._controller.start(port = port)
    return True

  def _command_address(self, cmd):
    print(self._controller.address)
    return True

  def _command_pid(self, cmd):
    print(self._controller.pid)
    return True
  
  def _command_version(self, cmd):
    print(self._controller.version)
    return True

  def _command_info(self, cmd):
    if not self._controller.address:
      print('not running')
      return True
    print('address: {}'.format(self._controller.address[0]))
    print('   port: {}'.format(self._controller.address[1]))
    print('    pid: {}'.format(self._controller.pid))
    print('version: {}'.format(self._controller.version))
    return True
  
  def _command_quit(self, cmd):
    return False
  
