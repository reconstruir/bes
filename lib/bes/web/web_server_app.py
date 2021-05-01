#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse

from bes.common.string_util import string_util
from bes.compat.input import input
from bes.system.log import log

from .web_server_controller import web_server_controller
from .file_web_server import file_web_server

class web_server_app(object):

  def __init__(self, server_class):
    log.add_logging(self, 'web_server')
    self._controller = web_server_controller(server_class)
  
  def main(self):
    ap = argparse.ArgumentParser()
    ap.add_argument('-p', '--port',
                    action = 'store',
                    default = None,
                    type = int,
                    help = 'The port to bind to [ None ]')
    args = ap.parse_args()
    if args.port:
      self._command_start([ 'start', str(args.port)])
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
    elif cmd[0] == 'port':
      return self._command_port(cmd)
    elif cmd[0] == 'quit':
      return self._command_quit(cmd)
    return True
  
  def _command_stop(self, cmd):
    self._controller.stop()
    return True

  def _command_start(self, cmd):
    if len(cmd) > 1:
      port = int(cmd[1])
    else:
      port = None
    self._controller.start(server_class = file_web_server, port = port)
    return True

  def _command_port(self, cmd):
    print(self._controller.address)
    return True
