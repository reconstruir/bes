#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.log import logger

from .vmware_vmrest import vmware_vmrest

class vmware_vmrest_controller(object):

  _log = logger('vmware_vmrest_controller')
  
  def __init__(self):
    self._server = None
    self.address = None
    
  def start(self, *args, **kargs):
    if self._server:
      return
    self._log.log_i('controller start: args=%s; kargs=%s' % (str(args), str(kargs)))
    self._server = vmware_vmrest(*args, **kargs)
    self._log.log_i('starting server.')
    self._server.start()
    self.address = self._server.address
    self._log.log_i('server started on %s' % (str(self.address)))
  
  def stop(self):
    if not self._server:
      return
    self._log.log_i('stopping server.')
    self._server.stop()
    self._server = None
    
  def fail_next_request(self, status_code):
    if not self._server:
      raise RuntimeError('server not running.')
    self._server.fail_next_request(status_code)
