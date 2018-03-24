#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import multiprocessing
from wsgiref.simple_server import make_server

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

class web_server(with_metaclass(ABCMeta, object)):

  def __init__(self, port = None):
    self.address = None
    self._process = None
    self._port_queue = multiprocessing.Queue()
    
  @abstractmethod
  def handle_request(self, environ, start_response):
    pass
    
  def _server_process(self):

    def _handler(environ, start_response):
      return self.handle_request(environ, start_response)
    httpd = make_server('', 0, _handler)
    httpd.allow_reuse_address = True
    address = httpd.socket.getsockname()
    self._port_queue.put(address)
    httpd.serve_forever()
    
  def start(self):
    self._process = multiprocessing.Process(name = 'web_server', target = self._server_process)
    self._process.daemon = True
    self._process.start()
    self.address = self._port_queue.get()
  
  def stop(self):
    self._process.terminate()
    self._process.join()
