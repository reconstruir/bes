#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import multiprocessing
from wsgiref import simple_server

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.system import log

class web_server(with_metaclass(ABCMeta, object)):

  class handler(simple_server.WSGIRequestHandler):

    def __init__(self, request, client_address, server):
      log.add_logging(self, 'web_server_handler')
      simple_server.WSGIRequestHandler.__init__(self, request, client_address, server)
      
    def log_message(self, format, *args):
      m = "%s - - [%s] %s\n" % (self.client_address[0],
                                self.log_date_time_string(),
                                format % args)
      self.log_i(m)
      
  def __init__(self, port, log_tag = None):
    log.add_logging(self, tag = log_tag or 'web_server')
    self.log_i('web_server(port=%s)' % (port))
    self._requested_port = port
    self.address = None
    self._process = None
    self._port_queue = multiprocessing.Queue()
    
  @abstractmethod
  def handle_request(self, environ, start_response):
    pass
    
  def _server_process(self):

    def _handler(environ, start_response):
      self.log_i('calling handle_request()')
      result = self.handle_request(environ, start_response)
      return result
    httpd = simple_server.make_server('', self._requested_port or 0, _handler, handler_class = self.handler)
    httpd.allow_reuse_address = True
    address = httpd.socket.getsockname()
    self.log_i('notifying that port is known')
    self._port_queue.put(address)
    self.log_i('calling serve_forever()')
    httpd.serve_forever()
    
  def start(self):
    self._process = multiprocessing.Process(name = 'web_server', target = self._server_process)
    self._process.daemon = True
    self._process.start()
    self.log_i('waiting for port known notification')
    self.address = self._port_queue.get()
  
  def stop(self):
    self._process.terminate()
    self._process.join()
