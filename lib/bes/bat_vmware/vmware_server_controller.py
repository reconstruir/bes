#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.log import logger

from .vmware_server import vmware_server

class vmware_server_controller(object):

  _log = logger('vmware_server_controller')
  
  def __init__(self):
    self._server = None
    self._reset()
    
  def start(self, *args, **kargs):
    if self._server:
      return
    self._log.log_i('controller start: args=%s; kargs=%s' % (str(args), str(kargs)))
    self._server = vmware_server(*args, **kargs)
    self._log.log_i('starting server.')
    self._server.start()
    self.address = self._server.address
    self.pid = self._server.pid
    self.version = self._server.version
    self._log.log_i('server started on %s' % (str(self.address)))
  
  def stop(self):
    if not self._server:
      return
    self._log.log_i('stopping server.')
    self._server.stop()
    self._reset()

  def _reset(self):
    self.address = None
    self.pid = None
    self.version = None
    self._server = None
