#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.web import web_server, web_server_controller
from bes.common import string_util
from bes.compat import input
from bes.system import log

class sample_web_server(web_server):

  def __init__(self, port = None):
    super(sample_web_server, self).__init__(port = port, log_tag = 'sample_web_server')
    
  def handle_request(self, environ, start_response):
    path_info = environ['PATH_INFO']
    self.log_i('handle_request(%s)' % (path_info))
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ['nice server: %s\n' % (path_info)]

class app(object):

  def __init__(self):
    log.add_logging(self, 'app')
    self._controller = web_server_controller(sample_web_server)
  
  def main(self):
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
    self._controller.start(port = port)
    return True

  def _command_port(self, cmd):
    print(self._controller.address)
    return True

if __name__ == '__main__':
  raise SystemExit(app().main())
