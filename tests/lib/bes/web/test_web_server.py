#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import urllib2
from bes.testing.unit_test import unit_test
from bes.web import web_server, web_server_controller

class test_web_server(unit_test):

  class test_web_server(web_server):

    def __init__(self, port = None):
      web_server.__init__(self, port = port, log_tag = 'test_web_server')
    
    def handle_request(self, environ, start_response):
      path_info = environ['PATH_INFO']
      self.log_i('handle_request(%s)' % (path_info))
      start_response('200 OK', [('Content-Type', 'text/html')])
      return ['nice server: %s\n' % (path_info)]

  def test_basic(self):
    server = web_server_controller(self.test_web_server)
    server.start(None)
    url = 'http://localhost:%d/foo' % (server.address[1])
    response = urllib2.urlopen(url).read().strip()
    self.assertEqual( 'nice server: /foo', response )
    server.stop()
    
if __name__ == '__main__':
  unit_test.main()
