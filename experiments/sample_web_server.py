#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.web import web_server
from bes.compat import input

class sample_web_server(web_server):

  def __init__(self, port = None):
    super(sample_web_server, self).__init__(port = port)
    
  def handle_request(self, environ, start_response):
    p = environ['PATH_INFO']
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b'nice server: %s\n' % (p)]
    
server = None
    
def main():
  global server
  while True:
    try:
      cmd = input('CMD> ')
      if cmd == 'stop':
        if server:
          server.stop()
        server = None
      elif cmd == 'start':
        if server:
          server.stop()
        server = sample_web_server()
        server.start()
        print('server started on %s' % (str(server.address)))
      elif cmd == 'quit':
        break
    except KeyboardInterrupt as ex:
      break
    except EOFError as ex:
      break
  if server:
    server.stop()
  return 0

if __name__ == '__main__':
  raise SystemExit(main())
