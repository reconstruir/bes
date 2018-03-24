#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, urllib2, urlparse
from bes.testing.unit_test import unit_test
from bes.web import web_server, web_server_controller

class test_web_server(unit_test):

  class test_web_server(web_server):

    def __init__(self, port = None):
      web_server.__init__(self, port = port, log_tag = 'test_web_server')
      self._count = 0
      
    def handle_request(self, environ, start_response):
      self._count += 1
      path_info = environ['PATH_INFO']
      self.log_i('handle_request(%s)' % (path_info))
      response = {
        'payload': 'nice server: %s\n' % (path_info),
        'count': self._count,
      }
      start_response('200 OK', [('Content-Type', 'text/html')])
      return [ json.dumps(response, indent = 2) ]

  def test_basic(self):
    server = web_server_controller(self.test_web_server)
    server.start(None)
    port = server.address[1]

    url = self._make_url(port, 'foo')
    content = urllib2.urlopen(url).read()
    response = json.loads(content)
    self.assertEqual( { 'payload': 'nice server: /foo\n', 'count': 1 }, response )

    url2 = self._make_url(port, 'bar/baz')
    content = urllib2.urlopen(url2).read()
    response = json.loads(content)
    self.assertEqual( { 'payload': 'nice server: /bar/baz\n', 'count': 2 }, response )
    
    server.stop()
    
  @classmethod
  def _make_url(clazz, port, p):
    base = 'http://localhost:%d' % (port)
    return urlparse.urljoin(base, p)

if __name__ == '__main__':
  unit_test.main()
