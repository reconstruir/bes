#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import log

class web_server_controller(object):

  def __init__(self, server_class):
    log.add_logging(self, 'web_server_controller')
    self._server_class = server_class
    self._server = None
    self.address = None
    
  def start(self, port):
    if self._server:
      return
    self.log_i('controller port = %s' % (port))
    self._server = self._server_class(port)
    self.log_i('starting server.')
    self._server.start()
    self.address = self._server.address
    self.log_i('server started on %s' % (str(self.address)))
  
  def stop(self):
    if not self._server:
      return
    self.log_i('stopping server.')
    self._server.stop()
    self._server = None
    
